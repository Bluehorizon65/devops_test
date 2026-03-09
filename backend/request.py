import requests
import json

url = "http://localhost:3000/solar"

payload = {
    "latitude": 10.933519651332348,
    "longitude": 76.74317650322091,
    "system_capacity_kw": 7.5,
    "year": 2024,
    "optimize_orientation": True,
    "electricity_rate_inr": 7.5,
    "budget_inr": 600000,
    "prefer_brand": "Jinko",
    "max_payback_years": 7,
    "location_name": "Karunya",
    "zoom_level": 6 
}

response = requests.post(url, json=payload)

print("Status Code:", response.status_code)
print("Response JSON:")
print(json.dumps(response.json(), indent=2))
