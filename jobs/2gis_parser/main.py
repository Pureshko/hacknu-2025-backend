from config import DEFAULT_REGION_ID, DEFAULT_RUBRICS
from get_items import get_items_by_rubric
from utils import append_to_csv, load_seen_ids, save_seen_ids
import time

def main():
    csv_name = "2gis_all.csv"
    seen_ids = load_seen_ids()
    print(f"[i] Загружено {len(seen_ids)} сохранённых ID")

    for rubric_id in DEFAULT_RUBRICS:
        print(f"\n🔍 Парсинг рубрики ID = {rubric_id}")

        try:
            items = get_items_by_rubric(
                rubric_id,
                DEFAULT_REGION_ID,
                page_size=50,
                max_pages=50,
                seen_ids=seen_ids
            )

            if items:
                append_to_csv(items, filename=csv_name)
                save_seen_ids(seen_ids)  # обновляем ID после каждой рубрики
                print(f"[+] Сохранено {len(items)} записей по рубрике {rubric_id}")
            else:
                print(f"[i] Нет новых объектов по рубрике {rubric_id}")

            time.sleep(1)  # защита от rate limit

        except KeyboardInterrupt:
            print("\n[!] Парсинг прерван пользователем. Прогресс сохранён.")
            save_seen_ids(seen_ids)
            break

        except Exception as e:
            print(f"[!] Ошибка при обработке рубрики {rubric_id}: {e}")
            save_seen_ids(seen_ids)
            continue

    print("\n✅ Парсинг завершён.")
    print(f"Всего уникальных ID: {len(seen_ids)}")

if __name__ == "__main__":
    main()



# from config import DEFAULT_REGION_ID, DEFAULT_RUBRICS
# from get_items import get_items_by_rubric
# from utils import append_to_csv, load_seen_ids, save_seen_ids

# def main():
#     csv_name = "2gis_all.csv"
#     seen_ids = load_seen_ids()
#     print(f"[i] Загружено {len(seen_ids)} сохранённых ID")

#     for rubric_id in DEFAULT_RUBRICS:
#         print(f"\n🔍 Парсинг рубрики ID = {rubric_id}")
#         items = get_items_by_rubric(rubric_id, DEFAULT_REGION_ID, page_size=50, max_pages=50, seen_ids=seen_ids)
#         append_to_csv(items, filename=csv_name)
#         print(f"[+] Сохранено {len(items)} записей по рубрике {rubric_id}")

#     print("\n✅ Все данные сохранены. Уникальных ID:", len(seen_ids))

# def main():
#     all_results = []

#     for query in DEFAULT_QUERIES:
#         print(f"\n🔍 Парсинг по запросу: {query}")
#         items = search_places(query=query, region_id=DEFAULT_REGION_ID, page_size=10)

#         # добавляем категорию, чтобы знать из какого запроса объект
#         for item in items:
#             item["category"] = query
#         all_results.extend(items)

#     # сохраняем общий CSV
#     save_to_csv(all_results, filename="2gis_all.csv")

#     print(f"\n✅ Готово! Всего объектов: {len(all_results)}")
