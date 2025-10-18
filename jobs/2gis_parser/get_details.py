import requests
import json
import time
from config import API_KEY



# def enrich_details(item_id: str):
#     """
#     Получает расширенную информацию об объекте по ID через 2GIS API.
#     Забирает только доступные публично поля: рейтинг, отзывы, описание, рубрики, график работы.
#     """
#     url = "https://catalog.api.2gis.com/3.0/items/byid"
#     params = {
#         "id": item_id,
#         "fields": "items.reviews,items.schedule,items.description,items.rubrics",
#         "key": API_KEY
#     }

#     try:
#         response = requests.get(url, params=params)
#         data = response.json()
#     except Exception as e:
#         print(f"[!] Ошибка при запросе byid для {item_id}: {e}")
#         return {}

#     if response.status_code != 200 or "result" not in data:
#         print(f"[!] Неверный ответ для {item_id}: {data}")
#         return {}


#     items = data["result"].get("items", [])
#     if not items:
#         return {}

#     item = items[0]

#     details = {
#         "rating": None,
#         "ratings_count": None,
#         "reviews_count": None,
#         "rubrics": None,
#         "schedule": None
#     }

#     # --- Рейтинг и количество отзывов ---
#     reviews = item.get("reviews", {})
#     if isinstance(reviews, dict):
#         general_rating = reviews.get("general_rating")
#         if isinstance(general_rating, dict):
#             details["rating"] = general_rating.get("value")
#         elif isinstance(general_rating, (int, float)):
#             details["rating"] = general_rating
#         details["ratings_count"] = reviews.get("general_review_count_with_stars")
#         details["reviews_count"] = reviews.get("general_review_count")

#     # --- Рубрики (категории) ---
#     rubrics = item.get("rubrics", [])

#     if isinstance(rubrics, list):
#         names = [r.get("name") for r in rubrics if r.get("name")]
#         details["rubrics"] = ", ".join(names) if names else None

#     # --- График работы ---
#     schedule = item.get("schedule")
#     if schedule:
#         details["schedule"] = str(schedule)

#     return details


BASE_URL = "https://catalog.api.2gis.com/3.0/items/byid"


def enrich_details(item_id: str):
    """
    Безопасно получает расширенную информацию об объекте 2GIS.
    Возвращает рейтинг, отзывы, рубрики, график работы.
    Не падает при сбоях и всегда возвращает корректный словарь.
    """
    params = {
        "id": item_id,
        "fields": "items.reviews,items.schedule,items.description,items.rubrics",
        "key": API_KEY
    }

    details = {
        "rating": None,
        "ratings_count": None,
        "reviews_count": None,
        "rubrics": None,
        "schedule": None
    }

    for attempt in range(3):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            if response.status_code != 200:
                print(f"[{item_id}] Ошибка {response.status_code}, попытка {attempt+1}")
                time.sleep(1)
                continue

            data = response.json()
            items = data.get("result", {}).get("items", [])
            if not items:
                print(f"[{item_id}] Пустой ответ API")
                return details

            item = items[0]

            # --- Рейтинг и отзывы ---
            reviews = item.get("reviews", {})
            if isinstance(reviews, dict):
                general_rating = reviews.get("general_rating")
                if isinstance(general_rating, dict):
                    details["rating"] = general_rating.get("value")
                elif isinstance(general_rating, (int, float)):
                    details["rating"] = general_rating
                details["ratings_count"] = reviews.get("general_review_count_with_stars")
                details["reviews_count"] = reviews.get("general_review_count")

            # --- Рубрики ---
            rubrics = item.get("rubrics", [])
            if isinstance(rubrics, list):
                names = [r.get("name") for r in rubrics if r.get("name")]
                details["rubrics"] = ", ".join(names) if names else None

            # --- График работы ---
            schedule = item.get("schedule")
            if schedule:
                details["schedule"] = json.dumps(schedule, ensure_ascii=False)

            return details

        except requests.exceptions.RequestException as e:
            print(f"[{item_id}] Ошибка сети ({attempt+1}/3): {e}")
            time.sleep(2)
        except Exception as e:
            print(f"[{item_id}] Неожиданная ошибка: {e}")
            return details

    print(f"[{item_id}] Не удалось получить данные после 3 попыток")
    return details