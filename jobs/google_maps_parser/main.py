from google_maps_client import GooglePlacesClient
import asyncio

async def main():
    async with GooglePlacesClient(api_key="YOUR_API_KEY") as gp:
        # одиночная точка
        rec = await gp.enrich_point(43.2220, 76.8512, region="Алматинская область")
        print(rec)

        # список точек
        many = await gp.enrich_many([(43.2220, 76.8512), (43.155, 76.93)], region="Алматы")
        print(len(many))

        # CSV
        count = await gp.enrich_csv("data/2gis_all.csv", "data/enriched_google.csv")
        print("Сохранено:", count)

if __name__ == "__main__":
    asyncio.run(main())