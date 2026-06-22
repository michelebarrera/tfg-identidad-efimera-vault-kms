# Deployment Guide

## 1. Objetivo

Esta guía describe el procedimiento seguido para desplegar el entorno utilizado durante el Trabajo Fin de Grado "Identidad efímera y autenticación mutua con HashiCorp Vault y AWS KMS".

El objetivo es reproducir una infraestructura capaz de emitir certificados X.509 de corta duración mediante HashiCorp Vault, proteger las claves maestras mediante AWS KMS y establecer comunicaciones autenticadas mediante Mutual TLS (mTLS).

---

## 2. Requisitos previos

### Software

* Ubuntu 24.04 (o WSL Ubuntu 24.04)
* Python 3.11+
* AWS CLI v2
* HashiCorp Vault 1.15.6
* OpenSSL

### Cuenta AWS

Es necesario disponer de:

* Una cuenta AWS activa.
* Permisos para utilizar AWS KMS.
* Credenciales configuradas mediante AWS CLI.

Verificar la configuración:

```bash
aws sts get-caller-identity
```

---

## 3. Configuración de AWS KMS

Crear una clave KMS desde la consola AWS o mediante AWS CLI:

```bash
aws kms create-key \
  --description "TFG Vault Auto-Unseal Key"
```

Guardar el ARN o Key ID generado.

Comprobar las claves disponibles:

```bash
aws kms list-keys
```

---

## 4. Configuración de Vault

### Descargar Vault

```bash
wget https://releases.hashicorp.com/vault/1.15.6/vault_1.15.6_linux_amd64.zip
unzip vault_1.15.6_linux_amd64.zip
sudo mv vault /usr/local/bin/
```

Verificar instalación:

```bash
vault version
```

### Configuración Auto-Unseal

Editar:

```text
vault/config/vault.hcl
```

Incluyendo la configuración AWS KMS utilizada durante el proyecto.

---

## 5. Arranque de Vault

Iniciar el servidor:

```bash
vault server -config=config/vault.hcl
```

En otra terminal:

```bash
export VAULT_ADDR="http://127.0.0.1:8200"
```

Inicializar Vault:

```bash
vault operator init
```

Guardar de forma segura:

* Unseal Keys
* Root Token

Desbloquear Vault:

```bash
vault operator unseal
```

Comprobar estado:

```bash
vault status
```

---

## 6. Configuración de la PKI

Habilitar motor PKI:

```bash
vault secrets enable pki
```

Configurar URLs:

```bash
vault write pki/config/urls \
 issuing_certificates="http://127.0.0.1:8200/v1/pki/ca" \
 crl_distribution_points="http://127.0.0.1:8200/v1/pki/crl"
```

Crear rol:

```bash
vault write pki/roles/tfg-service \
 allowed_domains="tfg.local" \
 allow_subdomains=true \
 max_ttl="30m"
```

---

## 7. Configuración de políticas

Cargar la política incluida en el repositorio:

```bash
vault policy write tfg-service-policy \
 policies/tfg-service-policy.hcl
```

Generar token para pruebas:

```bash
vault token create \
 -policy=tfg-service-policy \
 -ttl=1h
```

Guardar el token generado.

---

## 8. Generación de certificados

### Certificado servidor

```bash
cd ~/TFG/mtls-demo/server
vault write -format=json pki/issue/tfg-service \
 common_name="mtls-server.tfg.local" \
 ttl="30m"
```
Extraer el certificado
```bash
cat server-response.json | jq -r '.data.certificate' > certs/server.crt cat server-response.json | jq -r '.data.private_key' > certs/server.key cat server-response.json | jq -r '.data.issuing_ca' > certs/ca.crt
```
Comprobar validez del certificado:
```bash
openssl x509 -in certs/server.crt -noout -dates -subject
```

### Certificado cliente

```bash
cd ~/TFG/mtls-demo/client
vault write -format=json pki/issue/tfg-service \
 common_name="lambda-client.tfg.local" \
 ttl="30m"
```
Extraer el certificado
```bash
cat client-response.json | jq -r '.data.certificate' > certs/client.crt cat client-response.json | jq -r '.data.private_key' > certs/client.key cat client-response.json | jq -r '.data.issuing_ca' > certs/ca.crt
```
Comprobar validez del certificado:
```bash
openssl x509 -in certs/client.crt -noout -dates -subject
```

---

## 9. Ejecución de la demostración mTLS

### Servidor

```bash
cd mtls-demo/server
python3 app.py
```

### Cliente

```bash
export VAULT_TOKEN="<TOKEN>"

cd mtls-demo/client
python3 client.py
```

La ejecución correcta debe mostrar una autenticación mutua satisfactoria y una respuesta HTTP 200.

---

## 10. Prueba de autorización

La aplicación implementa una política básica basada en la identidad obtenida del certificado cliente.

Identidad autorizada:

```text
lambda-client.tfg.local
```

Identidades no autorizadas:

```text
evil-client.tfg.local
```

Las identidades no autorizadas deben recibir una respuesta HTTP 403.

---

## 11. Evaluación de rendimiento

### HTTPS convencional

Terminal 1:

```bash
python3 vault/app_timing_https.py
```

Terminal 2:

```bash
python3 vault/client_timing_https.py
```

### Flujo completo Vault + mTLS

Terminal 1:

```bash
python3 vault/app_timing_mtls.py
```

Terminal 2:

```bash
export VAULT_TOKEN="<TOKEN>"
python3 vault/client_timing_mtls.py
```

Los scripts generan automáticamente las métricas utilizadas en la evaluación experimental presentada en la memoria.

---

## 12. Resultados esperados

La infraestructura desplegada debe permitir:

* Emisión dinámica de certificados X.509.
* Identidades efímeras con TTL de 30 minutos.
* Autenticación mutua mediante mTLS.
* Autorización basada en identidad.
* Protección criptográfica mediante AWS KMS.
* Evaluación del impacto temporal introducido por el modelo.
