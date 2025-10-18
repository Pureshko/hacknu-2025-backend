import requests
import time
from urllib.parse import urlencode
from config import API_KEY
from get_coordinates import get_lat_and_lon
from get_details import enrich_details

BASE_URL = "https://catalog.api.2gis.com/3.0/items"


def get_items_by_rubric(
    rubric_id: str,
    region_id: str,
    page_size: int = 50,
    max_pages: int = 10,
    seen_ids=None
):
    """
    Безопасно получает объекты по rubric_id.
    - Не ломается при сетевых ошибках.
    - Пропускает проблемные страницы и продолжает дальше.
    - Не добавляет дубликаты (через seen_ids).
    """
    if seen_ids is None:
        seen_ids = set()

    all_items = []

    for page in range(1, max_pages + 1):
        params = {
            "rubric_id": rubric_id,
            "region_id": region_id,
            "page_size": page_size,
            "page": page,
            "fields": "items.point,items.address,items.reviews,items.schedule",
            "key": API_KEY
        }

        # --- запрос с повторными попытками ---
        for attempt in range(3):
            try:
                response = requests.get(BASE_URL, params=params, timeout=10)
                if response.status_code != 200:
                    print(f"[{rubric_id}] Ошибка {response.status_code} на странице {page}, попытка {attempt+1}")
                    time.sleep(1)
                    continue
                data = response.json()
                break
            except requests.exceptions.RequestException as e:
                print(f"[{rubric_id}] Ошибка сети ({attempt+1}/3): {e}")
                time.sleep(2)
        else:
            print(f"[{rubric_id}] Пропущена страница {page} после 3 попыток")
            continue

        # --- проверяем есть ли результат ---
        result = data.get("result", {})
        items = result.get("items", [])
        if not items:
            print(f"[{rubric_id}] Страница {page} пуста, завершаем парсинг рубрики.")
            break  # данных больше нет → останавливаем цикл

        # --- основной парсинг объектов ---
        for item in items:
            item_id = item.get("id")
            if not item_id or item_id in seen_ids:
                continue
            seen_ids.add(item_id)

            address = item.get("address_name")
            lat = item.get("point", {}).get("lat")
            lon = item.get("point", {}).get("lon")

            if not lat or not lon:
                lat, lon = get_lat_and_lon(address, region_id)

            info = {
                "id": item_id,
                "name": item.get("name"),
                "address": address,
                "lat": lat,
                "lon": lon,
                "rubric_id": rubric_id,
                "rating": None,
                "ratings_count": None,
                "reviews_count": None,
                "schedule": None
            }

            try:
                details = enrich_details(item_id)
                if details:
                    info.update(details)
            except Exception as e:
                print(f"[{rubric_id}] enrich_details({item_id}) вызвал ошибку: {e}")

            all_items.append(info)

        print(f"[{rubric_id}] Страница {page}: {len(items)} объектов обработано")

        # --- проверяем, есть ли следующая страница ---
        has_next = result.get("has_next_page")
        if has_next is False:
            print(f"[{rubric_id}] Достигнут конец данных (стр. {page}).")
            break

        time.sleep(0.5)


    return all_items


# def get_items_by_rubric(rubric_id: str, region_id: str, page_size: int = 50, max_pages: int = 10, seen_ids=None):
#     if seen_ids is None:
#         seen_ids = set()

#     all_items = []

#     for page in range(1, max_pages + 1):
#         params = {
#             "rubric_id": rubric_id,
#             "region_id": region_id,
#             "page_size": page_size,
#             "page": page,
#             "fields": "items.point,items.address,items.reviews,items.schedule",
#             "key": API_KEY
#         }

#         response = requests.get(BASE_URL, params=params)
#         data = response.json()

#         if response.status_code != 200 or "result" not in data:
#             print(f"[!] Ошибка запроса по рубрике {rubric_id} (стр. {page}):", data)
#             break

#         items = data["result"].get("items", [])
#         if not items:
#             break  # больше страниц нет

#         for item in items:
#             item_id = item.get("id")
#             if item_id in seen_ids:
#                 continue
#             seen_ids.add(item_id)

#             address = item.get("address_name")
#             lat = item.get("point", {}).get("lat")
#             lon = item.get("point", {}).get("lon")

#             if not lat or not lon:
#                 lat, lon = get_lat_and_lon(address, region_id)


#             info = {
#                 "name": item.get("name"),
#                 "address": item.get("address_name"),
#                 "lat": lat,
#                 "lon": lon,
#                 "rubric_id": rubric_id,
#                 "rating": None,
#                 "ratings_count": None,
#                 "reviews_count": None,
#                 "schedule": None
#             }

#             details = enrich_details(item["id"])
#             info.update(details)
#             all_items.append(info)

#         #print(f"[{rubric_id}] Страница {page}: {len(items)} объектов")

#     return all_items


# # def search_places(query: str, region_id: str, page_size: int = 10, page: int = 1):
# #     params = {
# #         "q": query,                     # поисковый запрос (например "глэмпинг" или "турбаза")
# #         "region_id": region_id,         # ID региона (например 67 для Алматы)
# #         "page_size": page_size,         # сколько объектов вернуть
# #         "page": page,                   # страница
# #         "fields": "items.point,items.address,items.contact_groups",
# #         "key": API_KEY
# #     }
# #     response = requests.get(BASE_URL, params=params)
# #     data = response.json()

# #     results = []
# #     if response.status_code == 200 and "result" in data:
# #         for item in data["result"]["items"]:
# #             #print(json.dumps(item, ensure_ascii=False, indent=2))
# #             address = item.get("address_name")
# #             lat = item.get("point", {}).get("lat")
# #             lon = item.get("point", {}).get("lon")

# #             # если координат нет — геокодируем
# #             if not lat or not lon:
# #                 lat, lon = get_lat_and_lon(address, region_id=region_id)

# #             info = {
# #                 "name": item.get("name"),
# #                 "address": address,
# #                 "lat": lat,
# #                 "lon": lon,
# #             }

# #             details = enrich_details(item["id"])
# #             info.update(details)

# #             # Parsing contacts
# #             # for group in item.get("contact_groups", []):
# #             #     for contact in group.get("contacts", []):
# #             #         if contact.get("type") == "phone":
# #             #             info["phone"] = contact.get("value")
# #             #         elif contact.get("type") == "website":
# #             #             info["website"] = contact.get("value")
            
# #             results.append(info)
    
# #     else:
# #         print("Query error:", data)
    
# #     return results

# if __name__ == '__main__':
#     query = "горы"
#     places = search_places(query=query, region_id=DEFAULT_REGION_ID, page_size=10)
#     #print(json.dumps(places, ensure_ascii=False, indent=2))