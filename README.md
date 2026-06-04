# TFG - Identidad Efímera y Autenticación Mutua con HashiCorp Vault y AWS KMS

Repositorio asociado al Trabajo Fin de Grado de Ingeniería Informática realizado en la Universidad Politécnica de Madrid.

## Descripción

Este proyecto implementa un modelo de identidad efímera basado en certificados X.509 de corta duración emitidos dinámicamente mediante HashiCorp Vault. La solución utiliza autenticación mutua TLS (mTLS) para proteger las comunicaciones entre servicios y AWS KMS para la protección criptográfica de las claves maestras empleadas por Vault.

## Estructura del repositorio

```text
TFG/
├── mtls-demo/
│   ├── client/
│   │   ├── client.py
│   │   └── requirements.txt
│   └── server/
│       └── app.py
│
└── vault/
    ├── app_timing_https.py
    ├── app_timing_mtls.py
    ├── client_timing_https.py
    ├── client_timing_mtls.py
    ├── config/
    │   └── vault.hcl
    └── policies/
        └── tfg-service-policy.hcl
```

## Requisitos

* Ubuntu 24.04 (WSL utilizado durante el desarrollo)
* Python 3.11 o superior
* HashiCorp Vault 1.15.6
* AWS CLI configurado
* Cuenta AWS con acceso a KMS
* Librerías Python:

  * hvac
  * requests

Instalación de dependencias:

```bash
pip install hvac requests
```

## Preparación del entorno AWS

La implementación utiliza AWS KMS como mecanismo de protección criptográfica para las claves maestras de HashiCorp Vault mediante la funcionalidad Auto-Unseal.

Antes de arrancar Vault es necesario disponer de:

* Una cuenta AWS con permisos sobre AWS KMS.
* Una clave KMS creada previamente.
* AWS CLI correctamente configurado.
* Credenciales válidas con permisos para utilizar la clave KMS.

Verificar la configuración de AWS CLI:

```bash
aws sts get-caller-identity
```

El resultado debe mostrar la identidad AWS utilizada durante la ejecución.

Verificar el acceso a KMS:

```bash
aws kms list-keys
```

Una vez comprobado el acceso, Vault podrá utilizar la clave KMS configurada en `config/vault.hcl` para realizar el proceso de Auto-Unseal.


## Arranque de HashiCorp Vault

Situarse en la carpeta del proyecto:

```bash
cd ~/TFG/vault
```

Iniciar Vault utilizando la configuración incluida:

```bash
vault server -config=config/vault.hcl
```

En una segunda terminal:

```bash
export VAULT_ADDR="http://127.0.0.1:8200"
```

Inicializar y desbloquear Vault siguiendo el procedimiento descrito en la memoria.

Verificar el estado:

```bash
vault status
```

## Ejecución del servicio protegido mediante mTLS

Situarse en la carpeta del servidor:

```bash
cd ~/TFG/mtls-demo/server
```

Ejecutar:

```bash
python3 app.py
```

El servidor quedará escuchando conexiones HTTPS protegidas mediante autenticación mutua TLS.

## Ejecución del cliente con identidad efímera

Situarse en la carpeta del cliente:

```bash
cd ~/TFG/mtls-demo/client
```

Configurar las variables de entorno necesarias:

```bash
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="<TOKEN>"
```

Ejecutar:

```bash
python3 client.py
```

El cliente solicitará dinámicamente un certificado X.509 a Vault y establecerá una conexión mTLS con el servicio receptor.

## Reproducción de la evaluación de rendimiento

### Escenario HTTPS convencional

Terminal 1:

```bash
cd ~/TFG/vault
python3 app_timing_https.py
```

Terminal 2:

```bash
cd ~/TFG/vault
python3 client_timing_https.py
```

### Escenario identidad efímera + mTLS

Terminal 1:

```bash
cd ~/TFG/vault
python3 app_timing_mtls.py
```

Terminal 2:

```bash
cd ~/TFG/vault

export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="<TOKEN>"

python3 client_timing_mtls.py
```

Los scripts calculan automáticamente los tiempos de ejecución medios, mínimos y máximos utilizados en la evaluación presentada en la memoria.

## Diagrama de arquitectura

<img width="890" height="409" alt="image" src="https://github.com/user-attachments/assets/63033f7c-44ff-40ba-b3ba-96f38ec15b5e" />


## Autor

Michele Barrera

Trabajo Fin de Grado - Universidad Politécnica de Madrid
