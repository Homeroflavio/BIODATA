import requests
import sys

print("Começando o teste...", flush=True)

try:
    resp = requests.get(
        "https://api.gbif.org/v1/occurrence/search",
        params={"scientificName": "Panthera onca", "limit": 5},
        timeout=15
    )
    print("Status code:", resp.status_code, flush=True)
    print("Primeiros 200 caracteres da resposta:", resp.text[:200], flush=True)
except Exception as erro:
    print("ERRO:", type(erro).__name__, str(erro), flush=True)

print("Teste terminou.", flush=True)