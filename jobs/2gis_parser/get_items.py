import requests
import json
from urllib.parse import urlencode
from config import API_KEY, DEFAULT_REGION_ID
from get_coordinates import get_lat_and_lon

BASE_URL = "https://catalog.api.2gis.com/3.0/items"


def search_places(query: str, region_id: str, page_size: int = 10, page: int = 1):
    params = {
        "q": query,                     # поисковый запрос (например "глэмпинг" или "турбаза")
        "region_id": region_id,         # ID региона (например 67 для Алматы)
        "page_size": page_size,         # сколько объектов вернуть
        "page": page,                   # страница
        "fields": "items.point,items.address,items.contact_groups",
        "key": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    results = []
    if response.status_code == 200 and "result" in data:
        for item in data["result"]["items"]:
            address = item.get("address_name")
            lat = item.get("point", {}).get("lat")
            lon = item.get("point", {}).get("lon")

            # если координат нет — геокодируем
            if not lat or not lon:
                lat, lon = get_lat_and_lon(address, region_id=region_id)

            info = {
                "name": item.get("name"),
                "address": address,
                "lat": lat,
                "lon": lon,
                "phone": None,
                "website": None
            }

            # Parsing contacts
            for group in item.get("contact_groups", []):
                for contact in group.get("contacts", []):
                    if contact.get("type") == "phone":
                        info["phone"] = contact.get("value")
                    elif contact.get("type") == "website":
                        info["website"] = contact.get("value")
            
            results.append(info)
    
    else:
        print("Query error:", data)
    
    return results

if __name__ == '__main__':
    query = "глэмпинг"
    places = search_places(query=query, region_id=DEFAULT_REGION_ID, page_size=10)
    print(json.dumps(places, ensure_ascii=False, indent=2))