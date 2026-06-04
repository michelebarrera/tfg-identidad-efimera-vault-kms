import os
import json
import tempfile
import requests
import hvac

VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

client = hvac.Client(
    url=VAULT_ADDR,
    token=VAULT_TOKEN
)

print("[+] Solicitando certificado dinamico a Vault...")

response = client.write(
    "pki/issue/tfg-service",
    common_name="lambda-client.tfg.local",
    ttl="30m"
)

certificate = response["data"]["certificate"]
private_key = response["data"]["private_key"]
issuing_ca = response["data"]["issuing_ca"]

print("[+] Certificado emitido correctamente")

with tempfile.NamedTemporaryFile(delete=False) as cert_file:
    cert_file.write(certificate.encode())
    cert_path = cert_file.name

with tempfile.NamedTemporaryFile(delete=False) as key_file:
    key_file.write(private_key.encode())
    key_path = key_file.name

with tempfile.NamedTemporaryFile(delete=False) as ca_file:
    ca_file.write(issuing_ca.encode())
    ca_path = ca_file.name

print("[+] Realizando peticion HTTPS con mTLS...")

url = "https://mtls-server.tfg.local:8443"

payload = {
    "mensaje": "Peticion automatizada desde cliente serverless"
}

response = requests.post(
    url,
    json=payload,
    cert=(cert_path, key_path),
    verify=ca_path
)

print("\n=== RESPUESTA SERVIDOR ===")
print(response.text)
