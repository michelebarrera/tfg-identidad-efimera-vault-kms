import os
import time
import tempfile
import statistics
import requests
import hvac

VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
URL = "https://mtls-server.tfg.local:8443"
ITERATIONS = 10

payload = {
    "mensaje": "Prueba de tiempo con certificado dinamico y mTLS"
}

vault_client = hvac.Client(
    url=VAULT_ADDR,
    token=VAULT_TOKEN
)

session = requests.Session()
session.trust_env = False

cert_times = []
mtls_times = []
total_times = []

for i in range(ITERATIONS):
    start_total = time.perf_counter()

    start_cert = time.perf_counter()

    response = vault_client.write(
        "pki/issue/tfg-service",
        common_name="lambda-client.tfg.local",
        ttl="30m"
    )

    certificate = response["data"]["certificate"]
    private_key = response["data"]["private_key"]
    issuing_ca = response["data"]["issuing_ca"]

    end_cert = time.perf_counter()

    with tempfile.NamedTemporaryFile(delete=False) as cert_file:
        cert_file.write(certificate.encode())
        cert_path = cert_file.name

    with tempfile.NamedTemporaryFile(delete=False) as key_file:
        key_file.write(private_key.encode())
        key_path = key_file.name

    with tempfile.NamedTemporaryFile(delete=False) as ca_file:
        ca_file.write(issuing_ca.encode())
        ca_path = ca_file.name

    start_mtls = time.perf_counter()

    mtls_response = session.post(
        URL,
        json=payload,
        cert=(cert_path, key_path),
        verify=ca_path
    )

    end_mtls = time.perf_counter()
    end_total = time.perf_counter()

    cert_elapsed = end_cert - start_cert
    mtls_elapsed = end_mtls - start_mtls
    total_elapsed = end_total - start_total

    cert_times.append(cert_elapsed)
    mtls_times.append(mtls_elapsed)
    total_times.append(total_elapsed)

    print(
        f"Prueba {i + 1}: "
        f"certificado={cert_elapsed:.6f} s | "
        f"mTLS={mtls_elapsed:.6f} s | "
        f"total={total_elapsed:.6f} s | "
        f"HTTP {mtls_response.status_code}"
    )

    os.remove(cert_path)
    os.remove(key_path)
    os.remove(ca_path)

print("\n=== RESULTADOS VAULT + mTLS ===")
print(f"Media solicitud certificado: {statistics.mean(cert_times):.6f} s")
print(f"Media invocacion mTLS: {statistics.mean(mtls_times):.6f} s")
print(f"Media total certificado + mTLS: {statistics.mean(total_times):.6f} s")

print(f"Maximo solicitud certificado: {max(cert_times):.6f} s")
print(f"Maximo invocacion mTLS: {max(mtls_times):.6f} s")
print(f"Maximo total certificado + mTLS: {max(total_times):.6f} s")