import os
import requests
from dotenv import load_dotenv

load_dotenv() 
api_key = os.getenv("IUCN_API_KEY")

headers = {"Authorization": f"Bearer {api_key}"}
url = "https://api.iucnredlist.org/api/v4/taxa/scientific_name"
params = {"genus_name": "Panthera", "species_name": "onca"}

resp = requests.get(url, headers=headers, params=params)
print(resp.status_code)
print(resp.json())