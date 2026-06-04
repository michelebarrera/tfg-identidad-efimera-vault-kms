import time
import statistics
import requests

URL = "https://mtls-server.tfg.local:8444"
ITERATIONS = 10

payload = {
    "mensaje": "Prueba de tiempo HTTPS normal"
}

times = []

session = requests.Session()
session.trust_env = False

for i in range(ITERATIONS):
    start = time.perf_counter()

    response = session.post(
        URL,
        json=payload,
        verify="certs/ca.crt"
    )

    end = time.perf_counter()
    elapsed = end - start
    times.append(elapsed)

    print(f"Prueba {i + 1}: {elapsed:.6f} s - HTTP {response.status_code}")

print("\n=== RESULTADOS HTTPS NORMAL ===")
print(f"Media: {statistics.mean(times):.6f} s")
print(f"Maximo: {max(times):.6f} s")
print(f"Minimo: {min(times):.6f} s")