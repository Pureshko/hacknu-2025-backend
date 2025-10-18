from config import DEFAULT_REGION_ID, DEFAULT_QUERIES
from get_items import search_places
from utils import save_to_csv

def main():
    all_results = []

    for query in DEFAULT_QUERIES:
        print(f"\n🔍 Парсинг по запросу: {query}")
        items = search_places(query=query, region_id=DEFAULT_REGION_ID, page_size=50)

        # добавляем категорию, чтобы знать из какого запроса объект
        for item in items:
            item["category"] = query
        all_results.extend(items)

    # сохраняем общий CSV
    save_to_csv(all_results, filename="2gis_all.csv")

    print(f"\n✅ Готово! Всего объектов: {len(all_results)}")

if __name__ == "__main__":
    main()
