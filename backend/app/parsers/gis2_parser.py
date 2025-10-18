import aiohttp
from typing import List, Dict
from app.config import get_settings

settings = get_settings()


class Gis2Parser:
    BASE_URL = "https://catalog.api.2gis.com/3.0"

    def __init__(self):
        self.api_key = settings.GIS2_API_KEY

    async def search_venues(
        self, query: str, region: str = "Алматы", limit: int = 50
    ) -> List[Dict]:
        """
        Поиск объектов через 2GIS Places API
        """
        url = f"{self.BASE_URL}/items"

        params = {
            "q": query,
            "region_id": await self._get_region_id(region),
            "key": self.api_key,
            "fields": "items.point,items.contact_groups,items.rubrics",
            "page_size": min(limit, 50),
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return self._parse_results(data)

    async def _get_region_id(self, region_name: str) -> int:
        """Получить ID региона"""
        # Алматы = 1, Астана = 2, и т.д.
        region_map = {
            "Алматы": 1,
            "Астана": 2,
            "Караганда": 164,
            "Шымкент": 165,
        }
        return region_map.get(region_name, 1)

    def _parse_results(self, data: Dict) -> List[Dict]:
        """Парсинг ответа от 2GIS"""
        venues = []

        for item in data.get("result", {}).get("items", []):
            venue = {
                "name": item.get("name"),
                "address": item.get("address_name"),
                "latitude": item.get("point", {}).get("lat"),
                "longitude": item.get("point", {}).get("lon"),
                "phone": None,
                "website": None,
                "source": "2gis",
            }

            # Извлечь контакты
            contacts = item.get("contact_groups", [])
            if contacts:
                for contact in contacts[0].get("contacts", []):
                    if contact.get("type") == "phone":
                        venue["phone"] = contact.get("text")
                    elif contact.get("type") == "website":
                        venue["website"] = contact.get("url")

            venues.append(venue)

        return venues