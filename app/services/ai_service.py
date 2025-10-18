from typing import Dict, Any
from openai import AsyncOpenAI
from ..core.config import settings


class AIService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_description(
        self, 
        accommodation: Dict[str, Any]
    ) -> str:
        """Generate SEO-optimized description for accommodation"""
        
        if not self.client:
            return self._fallback_description(accommodation)
        
        prompt = self._build_description_prompt(accommodation)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты эксперт по туристическому маркетингу "
                            "в Казахстане. Создай привлекательное, "
                            "SEO-оптимизированное описание для "
                            "туристического объекта размещения."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating description: {e}")
            return self._fallback_description(accommodation)
    
    def _build_description_prompt(
        self, 
        accommodation: Dict[str, Any]
    ) -> str:
        """Build prompt for description generation"""
        
        accommodation_types = {
            "luxury_glamping": "люкс глэмпинг",
            "family_guest_house": "семейный гостевой дом",
            "eco_tourism": "эко-туристический объект",
            "ethno_tourism": "этно-туристический объект (юрта)",
            "mountain_house": "горный домик"
        }
        
        type_ru = accommodation_types.get(
            accommodation.get("accommodation_type", ""),
            "объект размещения"
        )
        
        amenities = accommodation.get('amenities', [])
        amenities_str = ', '.join(amenities) if amenities else 'Не указано'
        
        prompt = f"""
Создай описание для следующего объекта:

Название: {accommodation.get('name', 'Без названия')}
Тип: {type_ru}
Локация: {accommodation.get('address', '')} ({accommodation.get('region', '')})
Удобства: {amenities_str}
Ценовой диапазон: {accommodation.get('price_min', '')} - {accommodation.get('price_max', '')} тенге

Требования:
- 150-300 слов
- Увлекательный и информативный стиль
- Подчеркни уникальные преимущества
- SEO-оптимизация (упоминание региона, типа размещения)
- Готово к публикации с минимальными правками
- На русском языке
"""
        return prompt
    
    def _fallback_description(
        self, 
        accommodation: Dict[str, Any]
    ) -> str:
        """Fallback description when AI is not available"""
        
        return (
            f"{accommodation.get('name', 'Объект размещения')} "
            f"расположен в {accommodation.get('region', 'Казахстане')}. "
            f"Прекрасное место для отдыха и релаксации."
        )
    
    def calculate_priority_score(
        self, 
        accommodation: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate priority scores for accommodation"""
        
        scores = {
            "online_activity_score": self._score_online_activity(
                accommodation
            ),
            "data_completeness_score": self._score_data_completeness(
                accommodation
            ),
            "popularity_score": self._score_popularity(accommodation),
            "commercial_potential_score": self._score_commercial_potential(
                accommodation
            ),
        }
        
        # Overall priority score (1-10)
        weights = {
            "online_activity_score": 0.25,
            "data_completeness_score": 0.20,
            "popularity_score": 0.30,
            "commercial_potential_score": 0.25
        }
        
        priority_score = sum(
            scores[key] * weights[key] 
            for key in scores
        )
        
        # Determine lead status
        if priority_score >= 8:
            lead_status = "hot"
        elif priority_score >= 5:
            lead_status = "warm"
        else:
            lead_status = "cold"
        
        return {
            **scores,
            "priority_score": round(priority_score, 2),
            "lead_status": lead_status
        }
    
    def _score_online_activity(self, acc: Dict) -> float:
        """Score online activity (0-10)"""
        score = 0
        
        if acc.get("instagram"):
            score += 3
        if acc.get("website"):
            score += 3
        if acc.get("telegram"):
            score += 2
        if acc.get("whatsapp"):
            score += 2
        
        return min(score, 10)
    
    def _score_data_completeness(self, acc: Dict) -> float:
        """Score data completeness (0-10)"""
        fields = [
            "name", "address", "phone", "latitude", "longitude",
            "photos", "description", "amenities", "price_min"
        ]
        
        filled = sum(1 for field in fields if acc.get(field))
        return (filled / len(fields)) * 10
    
    def _score_popularity(self, acc: Dict) -> float:
        """Score popularity (0-10)"""
        score = 0
        
        rating = acc.get("rating", 0)
        review_count = acc.get("review_count", 0)
        
        if rating >= 4.5:
            score += 4
        elif rating >= 4.0:
            score += 3
        elif rating >= 3.5:
            score += 2
        
        if review_count >= 50:
            score += 4
        elif review_count >= 20:
            score += 3
        elif review_count >= 5:
            score += 2
        
        photo_count = len(acc.get("photos", []))
        if photo_count >= 10:
            score += 2
        elif photo_count >= 5:
            score += 1
        
        return min(score, 10)
    
    def _score_commercial_potential(self, acc: Dict) -> float:
        """Score commercial potential (0-10)"""
        score = 5  # Base score
        
        # Premium accommodation types score higher
        if acc.get("accommodation_type") == "luxury_glamping":
            score += 3
        elif acc.get("accommodation_type") == "eco_tourism":
            score += 2
        
        # Price range indicates willingness to invest
        price_min = acc.get("price_min", 0)
        if price_min >= 30000:
            score += 2
        elif price_min >= 15000:
            score += 1
        
        return min(score, 10)