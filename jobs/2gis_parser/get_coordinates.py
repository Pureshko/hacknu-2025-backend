import requests
import json
from urllib.parse import urlencode
from config import API_KEY

BASE_URL = "https://catalog.api.2gis.com/3.0/items/geocode"

def get_lat_and_lon(address: str,  region_id: str, fields: str = "items.point"):
    params = {
        "q": address,
        "fields": fields,
        "region_id": region_id,
        "key": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200 and "result" in data:
        items = data["result"].get("items", [])
        if items and "point" in items[0]:
            lat = items[0]["point"]["lat"]
            lon = items[0]["point"]["lon"]
            return lat, lon
    
    print(f"[!] Не удалось получить координаты для: {address}")
    return None, None