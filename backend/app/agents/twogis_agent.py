from typing import Dict, List, Any
from .base_agent import BaseAgent
from ..core.config import settings
import asyncio


class TwoGISAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.api_key = settings.TWOGIS_API_KEY
        self.places_url = settings.TWOGIS_PLACES_API
        self.geocoder_url = settings.TWOGIS_GEOCODER_API
    
    async def search(
        self, 
        query: str, 
        region: str
    ) -> List[Dict[str, Any]]:
        """Search for accommodations in 2GIS"""
        
        # Search queries for different types
        search_queries = [
            f"{query} {region}",
            f"глэмпинг {region}",
            f"гостевой дом {region}",
            f"юрта {region}",
            f"эко коттедж {region}",
            f"база отдыха {region}"
        ]
        
        results = []
        
        for search_query in search_queries:
            params = {
                "q": search_query,
                "key": self.api_key,
                "fields": "items.point,items.address,items.contact_groups,"
                         "items.rubrics,items.name_ex,items.reviews",
                "page_size": 50
            }
            
            try:
                data = await self.rate_limited_request(
                    self.places_url, 
                    params
                )
                
                if "result" in data and "items" in data["result"]:
                    for item in data["result"]["items"]:
                        accommodation = self._parse_item(item, region)
                        if accommodation:
                            results.append(accommodation)
                
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"Error searching 2GIS: {e}")
        
        return results
    
    def _parse_item(
        self, 
        item: Dict, 
        region: str
    ) -> Dict[str, Any]:
        """Parse 2GIS item into accommodation format"""
        
        point = item.get("point", {})
        address_obj = item.get("address", {})
        contact_groups = item.get("contact_groups", [])
        
        # Extract contacts
        phone = None
        website = None
        
        for group in contact_groups:
            for contact in group.get("contacts", []):
                if contact.get("type") == "phone":
                    phone = contact.get("text")
                elif contact.get("type") == "website":
                    website = contact.get("url")
        
        # Determine accommodation type based on rubrics
        rubrics = [r.get("name", "") for r in item.get("rubrics", [])]
        accommodation_type = self._classify_type(
            item.get("name", ""), 
            rubrics
        )
        
        return {
            "name": item.get("name", ""),
            "twogis_id": item.get("id"),
            "latitude": point.get("lat"),
            "longitude": point.get("lon"),
            "address": address_obj.get("name"),
            "region": region,
            "phone": phone,
            "website": website,
            "accommodation_type": accommodation_type,
            "data_sources": ["2gis"],
            "reviews": item.get("reviews", {}),
            "rating": item.get("reviews", {}).get("rating")
        }
    
    def _classify_type(self, name: str, rubrics: List[str]) -> str:
        """Classify accommodation type"""
        name_lower = name.lower()
        rubrics_text = " ".join(rubrics).lower()
        
        if "глэмпинг" in name_lower or "glamping" in name_lower:
            if "люкс" in name_lower or "premium" in name_lower:
                return "luxury_glamping"
            return "eco_tourism"
        elif "юрта" in name_lower or "yurt" in name_lower:
            return "ethno_tourism"
        elif "гостевой дом" in name_lower or "guest house" in name_lower:
            return "family_guest_house"
        elif "горный" in name_lower or "mountain" in name_lower:
            return "mountain_house"
        elif "эко" in name_lower or "eco" in name_lower:
            return "eco_tourism"
        else:
            return "family_guest_house"
    
    async def enrich_data(
        self, 
        accommodation_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about accommodation"""
        
        params = {
            "id": accommodation_id,
            "key": self.api_key,
            "fields": "items.point,items.address,items.contact_groups,"
                     "items.rubrics,items.name_ex,items.reviews,"
                     "items.photos,items.schedule,items.attributes"
        }
        
        try:
            data = await self.rate_limited_request(
                self.places_url, 
                params
            )
            
            if "result" in data and "items" in data["result"]:
                item = data["result"]["items"][0]
                
                photos = []
                if "photos" in item:
                    photos = [
                        photo.get("url") 
                        for photo in item["photos"]
                    ]
                
                amenities = []
                if "attributes" in item:
                    amenities = [
                        attr.get("name") 
                        for attr in item["attributes"]
                    ]
                
                return {
                    "photos": photos,
                    "amenities": amenities,
                    "schedule": item.get("schedule", {})
                }
        
        except Exception as e:
            print(f"Error enriching data from 2GIS: {e}")
        
        return {}