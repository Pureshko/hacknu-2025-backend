import requests
import json
from urllib.parse import urlencode
from config import API_KEY
import time 

BASE_URL = "https://catalog.api.2gis.com/3.0/items/geocode"

def get_lat_and_lon(address: str,  region_id: str, fields: str = "items.point"):
    if not address:
        return None, None

    params = {
        "q": address,
        "fields": fields,
        "region_id": region_id,
        "key": API_KEY
    }

    for attempt in range(3):  # до трёх попыток при сетевых сбоях
        try:
            response = requests.get(BASE_URL, params=params, timeout=8)
            if response.status_code != 200:
                print(f"[!] Ошибка {response.status_code} при запросе координат для {address}")
                time.sleep(1)
                continue

            data = response.json()
            if not isinstance(data, dict) or "result" not in data:
                print(f"[!] Неожиданный формат ответа для {address}: {data}")
                return None, None

            items = data["result"].get("items", [])
            if items and "point" in items[0]:
                lat = items[0]["point"].get("lat")
                lon = items[0]["point"].get("lon")
                return lat, lon

            # если данных нет, выходим без исключения
            print(f"[!] Координаты не найдены для: {address}")
            return None, None

        except requests.exceptions.RequestException as e:
            print(f"[!] Ошибка соединения ({attempt+1}/3): {e}")
            time.sleep(2)  # пауза перед повтором
        except Exception as e:
            print(f"[!] Неожиданная ошибка при геокодировании '{address}': {e}")
            return None, None

    # если все три попытки не удались
    print(f"[!] Не удалось получить координаты после 3 попыток: {address}")
    return None, None