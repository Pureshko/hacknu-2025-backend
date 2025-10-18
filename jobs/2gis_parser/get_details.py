import requests
import json
from config import API_KEY

# def enrich_details(item_id: str):
#     url = "https://catalog.api.2gis.com/3.0/items/byid"
#     params = {
#         "id": item_id,
#         "fields": "items.contact_groups,items.reviews,items.schedule",
#         "key": API_KEY
#     }
#     r = requests.get(url, params=params).json()
#     if "result" in r and r["result"]["items"]:
#         item = r["result"]["items"][0]
#         contacts = {"phone": None, "website": None}
#         for group in item.get("contact_groups", []):
#             for c in group.get("contacts", []):
#                 if c.get("type") == "phone":
#                     contacts["phone"] = c.get("value")
#                 elif c.get("type") in ("website", "url"):
#                     contacts["website"] = c.get("value")
#         return contacts
#     return {"phone": None, "website": None}


def enrich_details(item_id: str):
    """
    Получает расширенную информацию об объекте по ID через 2GIS API.
    Забирает только доступные публично поля: рейтинг, отзывы, описание, рубрики, график работы.
    """
    url = "https://catalog.api.2gis.com/3.0/items/byid"
    params = {
        "id": item_id,
        "fields": "items.reviews,items.schedule,items.description,items.rubrics",
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        print(f"[!] Ошибка при запросе byid для {item_id}: {e}")
        return {}

    if response.status_code != 200 or "result" not in data:
        print(f"[!] Неверный ответ для {item_id}: {data}")
        return {}

    print(json.dumps(data, ensure_ascii=False, indent=2))
    items = data["result"].get("items", [])
    if not items:
        return {}

    item = items[0]

    details = {
        "rating": None,
        "ratings_count": None,
        "reviews_count": None,
        "description": None,
        "rubrics": None,
        "schedule": None
    }

    # --- Рейтинг и количество отзывов ---
    reviews = item.get("reviews", {})
    if isinstance(reviews, dict):
        general_rating = reviews.get("general_rating")
        if isinstance(general_rating, dict):
            details["rating"] = general_rating.get("value")
        elif isinstance(general_rating, (int, float)):
            details["rating"] = general_rating
        details["ratings_count"] = reviews.get("general_review_count_with_stars")
        details["reviews_count"] = reviews.get("general_review_count")

    # --- Описание ---
    description = item.get("description")
    if isinstance(description, str):
        details["description"] = description.strip()

    # --- Рубрики (категории) ---
    rubrics = item.get("rubrics", [])
    if isinstance(rubrics, list):
        names = [r.get("name") for r in rubrics if r.get("name")]
        details["rubrics"] = ", ".join(names) if names else None

    # --- График работы ---
    schedule = item.get("schedule")
    if schedule:
        details["schedule"] = str(schedule)

    return details