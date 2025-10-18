from openai import AsyncOpenAI
from app.config import get_settings
from app.models import LeadStatus, CategoryEnum
from typing import Dict, Tuple

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class ScoringAgent:
    """AI-агент для оценки и приоритизации объектов"""

    async def score_venue(self, venue_data: Dict) -> Tuple[float, LeadStatus]:
        """
        Оценивает объект по 10-бальной шкале и определяет статус лида
        """
        # Базовый скоринг без AI (быстро)
        base_score = self._calculate_base_score(venue_data)

        # AI-скоринг для более точной оценки
        ai_score = await self._ai_enhanced_scoring(venue_data)

        # Итоговый скор (средневзвешенное)
        final_score = base_score * 0.4 + ai_score * 0.6

        # Определяем статус
        lead_status = self._determine_lead_status(final_score, venue_data)

        return round(final_score, 2), lead_status

    def _calculate_base_score(self, venue_data: Dict) -> float:
        """Базовый скоринг на основе доступных данных"""
        score = 5.0  # Начальный балл

        # Полнота контактных данных (+2 балла макс)
        if venue_data.get("phone"):
            score += 0.5
        if venue_data.get("email"):
            score += 0.5
        if venue_data.get("website"):
            score += 0.5
        if venue_data.get("instagram"):
            score += 0.5

        # Наличие фото (+1 балл)
        photos = venue_data.get("photos", [])
        score += min(len(photos) * 0.2, 1.0)

        # Рейтинг и отзывы (+1.5 балла макс)
        rating = venue_data.get("rating", 0)
        if rating >= 4.5:
            score += 1.0
        elif rating >= 4.0:
            score += 0.5

        reviews = venue_data.get("reviews_count", 0)
        if reviews >= 50:
            score += 0.5

        # Ценовой диапазон (+0.5)
        if venue_data.get("price_min") and venue_data.get("price_max"):
            score += 0.5

        return min(score, 10.0)

    async def _ai_enhanced_scoring(self, venue_data: Dict) -> float:
        """AI-анализ для более точной оценки потенциала"""

        prompt = f"""Оцени потенциал этого туристического объекта для платформы MyTravel.kz по шкале от 1 до 10.

Объект:
- Название: {venue_data.get('name', 'Не указано')}
- Категория: {venue_data.get('category', 'Не указано')}
- Адрес: {venue_data.get('address', 'Не указано')}
- Контакты: {'Есть' if venue_data.get('phone') else 'Нет'}
- Сайт: {'Есть' if venue_data.get('website') else 'Нет'}
- Инстаграм: {'Есть' if venue_data.get('instagram') else 'Нет'}
- Описание: {venue_data.get('description', 'Не указано')[:200]}
- Рейтинг: {venue_data.get('rating', 'Нет')}
- Отзывов: {venue_data.get('reviews_count', 0)}

Критерии оценки:
1. Коммерческий потенциал (готовность платить за продвижение)
2. Привлекательность для туристов
3. Профессионализм бизнеса
4. Уникальность предложения

Ответь ТОЛЬКО числом от 1 до 10 (например: 8.5)"""

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10,
            )

            score_text = response.choices[0].message.content.strip()
            return float(score_text)

        except Exception as e:
            print(f"AI scoring error: {e}")
            return 5.0  # Fallback

    def _determine_lead_status(
        self, score: float, venue_data: Dict
    ) -> LeadStatus:
        """Определяет горячий/теплый/холодный лид"""

        # Горячий лид (8+)
        if score >= 8.0:
            return LeadStatus.HOT

        # Теплый лид (6-7.9)
        elif score >= 6.0:
            return LeadStatus.WARM

        # Холодный лид (<6)
        else:
            return LeadStatus.COLD

    def categorize_venue(self, venue_data: Dict) -> CategoryEnum:
        """Автоматическая категоризация объекта"""

        name = venue_data.get("name", "").lower()
        description = venue_data.get("description", "").lower()
        text = f"{name} {description}"

        # Простая эвристика (можно улучшить через AI)
        if any(
            word in text
            for word in ["люкс", "premium", "премиум", "villa", "вилла"]
        ):
            return CategoryEnum.LUXURY_GLAMPING

        elif any(word in text for word in ["юрта", "yurt", "этно"]):
            return CategoryEnum.ETHNO_TOURISM

        elif any(
            word in text for word in ["эко", "eco", "природа", "forest"]
        ):
            return CategoryEnum.ECOTOURISM

        elif any(
            word in text
            for word in ["семейный", "детский", "family", "kids"]
        ):
            return CategoryEnum.FAMILY_GUESTHOUSE

        elif any(word in text for word in ["горы", "mountain", "альпы"]):
            return CategoryEnum.MOUNTAIN_HOUSE

        # По умолчанию
        return CategoryEnum.ECOTOURISM