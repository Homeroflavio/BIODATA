import requests
import json

resp = requests.get(
    "https://api.gbif.org/v1/occurrence/search",
    params={"scientificName": "Panthera onca", "limit": 5}
)
dados = resp.json()

print(json.dumps(dados["results"][0], indent=2, ensure_ascii=False))