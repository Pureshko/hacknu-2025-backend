from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from ..core.config import settings
import asyncio
import aiohttp


class GooglePlacesAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        
        # Google Places API endpoints
        self.nearby_search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        self.photo_url = "https://maps.googleapis.com/maps/api/place/photo"
        
        # Almaty coordinates (center)
        self.almaty_center = {
            "lat": 43.2220,
            "lng": 76.8512
        }
        
        # Search radius (in meters) - 50km
        self.search_radius = 50000
    
    async def search(
        self, 
        query: str, 
        region: str
    ) -> List[Dict[str, Any]]:
        """Search for accommodations using Google Places API"""
        
        # Define search queries for different categories
        search_queries = [
            "глэмпинг в алматы",
            "юрты алматы",
            "eco lodge Almaty",
            "природа Almaty",
            "коттэджи алматы",
            "vacation rental Almaty mountains",
            "eco tourism Almaty",
            "mountain resort Almaty",
            "горы алматы"
        ]
        
        all_results = []
        seen_place_ids = set()
        
        for search_query in search_queries:
            try:
                # Text search
                results = await self._text_search(search_query)
                
                for place in results:
                    place_id = place.get('place_id')
                    
                    # Avoid duplicates
                    if place_id in seen_place_ids:
                        continue
                    
                    seen_place_ids.add(place_id)
                    
                    # Get detailed information
                    details = await self._get_place_details(place_id)
                    
                    if details:
                        accommodation = self._parse_place(details, region)
                        if accommodation:
                            all_results.append(accommodation)
                
                # Respect rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error searching Google Places: {e}")
        
        return all_results
    
    async def _text_search(self, query: str) -> List[Dict]:
        """Perform text search"""
        params = {
            'query': query,
            'key': self.api_key,
            'location': f"{self.almaty_center['lat']},{self.almaty_center['lng']}",
            'radius': self.search_radius,
            'language': 'ru'
        }
        
        try:
            data = await self.rate_limited_request(
                self.text_search_url, 
                params
            )
            return data.get('results', [])
        except Exception as e:
            print(f"Text search error: {e}")
            return []
    
    async def _nearby_search(
        self, 
        location: Dict[str, float], 
        place_type: str = "lodging"
    ) -> List[Dict]:
        """Perform nearby search"""
        params = {
            'location': f"{location['lat']},{location['lng']}",
            'radius': self.search_radius,
            'type': place_type,
            'key': self.api_key,
            'language': 'ru'
        }
        
        try:
            data = await self.rate_limited_request(
                self.nearby_search_url, 
                params
            )
            return data.get('results', [])
        except Exception as e:
            print(f"Nearby search error: {e}")
            return []
    
    async def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a place"""
        params = {
            'place_id': place_id,
            'fields': (
                'name,formatted_address,geometry,photos,'
                'rating,reviews,user_ratings_total,types,'
                'website,formatted_phone_number,opening_hours,'
                'price_level,editorial_summary,business_status,'
                'url,vicinity'
            ),
            'key': self.api_key,
            'language': 'ru'
        }
        
        try:
            data = await self.rate_limited_request(
                self.details_url, 
                params
            )
            return data.get('result')
        except Exception as e:
            print(f"Details error: {e}")
            return None
    
    def _parse_place(
        self, 
        place: Dict, 
        region: str
    ) -> Optional[Dict[str, Any]]:
        """Parse Google Place into our accommodation format"""
        
        # Extract basic info
        name = place.get('name', '')
        
        # Skip if not accommodation-related
        if not self._is_accommodation(name, place):
            return None
        
        # Get location
        geometry = place.get('geometry', {})
        location = geometry.get('location', {})
        
        # Extract photos
        photos = self._extract_photos(place.get('photos', []))
        
        # Extract reviews
        reviews_data = self._extract_reviews(place.get('reviews', []))
        
        # Determine category
        category = self._classify_category(name, place.get('types', []))
        
        # Extract price range (estimate)
        price_min, price_max = self._estimate_prices(
            place.get('price_level'),
            category
        )
        
        # Extract amenities/infrastructure
        amenities = self._extract_amenities(place)
        
        return {
            'name': name,
            'google_place_id': place.get('place_id'),
            'accommodation_type': category,
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'address': place.get('formatted_address', ''),
            'region': region,
            'phone': place.get('formatted_phone_number'),
            'website': place.get('website'),
            'description': self._create_description(place),
            'price_min': price_min,
            'price_max': price_max,
            'photos': photos,
            'rating': place.get('rating'),
            'review_count': place.get('user_ratings_total', 0),
            'reviews': reviews_data,
            'amenities': amenities,
            'data_sources': ['google_places'],
            'business_status': place.get('business_status', 'OPERATIONAL'),
            'google_maps_url': place.get('url'),
        }
    
    def _is_accommodation(self, name: str, place: Dict) -> bool:
        """Check if place is an accommodation"""
        name_lower = name.lower()
        types = place.get('types', [])
        
        # Keywords for accommodations
        accommodation_keywords = [
            'glamping', 'глэмпинг', 'yurt', 'юрта',
            'guest house', 'гостевой дом', 'cottage', 'коттедж',
            'lodge', 'resort', 'база отдыха', 'турбаза',
            'eco', 'эко', 'camp', 'кемпинг'
        ]
        
        # Check name
        for keyword in accommodation_keywords:
            if keyword in name_lower:
                return True
        
        # Check types
        accommodation_types = [
            'lodging', 'campground', 'rv_park', 
            'tourist_attraction', 'point_of_interest'
        ]
        
        return any(t in types for t in accommodation_types)
    
    def _classify_category(
        self, 
        name: str, 
        types: List[str]
    ) -> str:
        """Classify accommodation into our categories"""
        name_lower = name.lower()
        
        # Glamping
        if any(k in name_lower for k in ['glamping', 'глэмпинг']):
            if any(k in name_lower for k in ['luxury', 'люкс', 'premium']):
                return 'luxury_glamping'
            return 'eco_tourism'
        
        # Yurts (Ethno-tourism)
        if any(k in name_lower for k in ['yurt', 'юрта', 'юртовый']):
            return 'ethno_tourism'
        
        # Mountain houses
        if any(k in name_lower for k in ['mountain', 'горный', 'alpine']):
            return 'mountain_house'
        
        # Eco-tourism
        if any(k in name_lower for k in ['eco', 'эко', 'nature', 'природ']):
            return 'eco_tourism'
        
        # Guest houses (default for family accommodations)
        return 'family_guest_house'
    
    def _extract_photos(self, photos: List[Dict]) -> List[str]:
        """Extract photo URLs"""
        photo_urls = []
        
        for photo in photos[:10]:  # Limit to 10 photos
            photo_reference = photo.get('photo_reference')
            if photo_reference:
                # Construct photo URL
                photo_url = (
                    f"{self.photo_url}?"
                    f"maxwidth=800&"
                    f"photo_reference={photo_reference}&"
                    f"key={self.api_key}"
                )
                photo_urls.append(photo_url)
        
        return photo_urls
    
    def _extract_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """Extract and format reviews"""
        formatted_reviews = []
        
        for review in reviews[:5]:  # Top 5 reviews
            formatted_reviews.append({
                'author': review.get('author_name'),
                'rating': review.get('rating'),
                'text': review.get('text'),
                'time': review.get('time'),
                'language': review.get('language', 'ru')
            })
        
        return formatted_reviews
    
    def _estimate_prices(
        self, 
        price_level: Optional[int],
        category: str
    ) -> tuple[Optional[float], Optional[float]]:
        """Estimate price range in KZT"""
        
        # Base prices by category (per night in KZT)
        base_prices = {
            'luxury_glamping': (40000, 100000),
            'family_guest_house': (15000, 35000),
            'eco_tourism': (20000, 50000),
            'ethno_tourism': (18000, 40000),
            'mountain_house': (25000, 60000),
        }
        
        base_min, base_max = base_prices.get(
            category, 
            (15000, 40000)
        )
        
        # Adjust by Google's price_level (0-4 scale)
        if price_level is not None:
            multiplier = 1 + (price_level * 0.3)
            base_min = int(base_min * multiplier)
            base_max = int(base_max * multiplier)
        
        return base_min, base_max
    
    def _extract_amenities(self, place: Dict) -> List[str]:
        """Extract amenities/infrastructure from place data"""
        amenities = []
        
        # From types
        types = place.get('types', [])
        if 'parking' in types or 'park' in types:
            amenities.append('Parking')
        
        # From opening hours
        if place.get('opening_hours'):
            amenities.append('24/7 Access')
        
        # Default amenities based on rating
        rating = place.get('rating', 0)
        if rating >= 4.0:
            amenities.extend(['Wi-Fi', 'Kitchen', 'Shower'])
        
        return amenities
    
    def _create_description(self, place: Dict) -> str:
        """Create description from place data"""
        name = place.get('name', '')
        address = place.get('vicinity', place.get('formatted_address', ''))
        
        # Editorial summary if available
        editorial = place.get('editorial_summary', {})
        if editorial:
            return editorial.get('overview', '')
        
        # Create basic description
        description = f"{name} расположен в {address}."
        
        rating = place.get('rating')
        if rating:
            description += f" Рейтинг: {rating}/5."
        
        return description
    
    async def enrich_data(
        self, 
        accommodation_id: str
    ) -> Dict[str, Any]:
        """Enrich accommodation data with additional details"""
        details = await self._get_place_details(accommodation_id)
        
        if not details:
            return {}
        
        return {
            'photos': self._extract_photos(details.get('photos', [])),
            'reviews': self._extract_reviews(details.get('reviews', [])),
            'amenities': self._extract_amenities(details),
            'opening_hours': details.get('opening_hours', {}),
        }