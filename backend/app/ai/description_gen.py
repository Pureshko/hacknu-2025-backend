from openai import AsyncOpenAI
from app.config import get_settings
from app.models import CategoryEnum

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OutreachGenerator:
    """Генератор персонализированных сообщений для привлечения"""

    async def generate_outreach(
        self, venue_data: dict, channel: str = "whatsapp"
    ) -> str:
        """
        Генерирует персонализированное сообщение
        channel: 'whatsapp', 'email', 'instagram', 'telegram'
        """

        templates = {
            "whatsapp": "короткое и дружелюбное",
            "email": "формальное и подробное",
            "instagram": "неформальное с эмодзи",
            "telegram": "лаконичное и понятное",
        }

        style = templates.get(channel, "дружелюбное")

        prompt = f"""Создай персонализированное сообщение для привлечения партнера на платформу MyTravel.kz.

Объект: {venue_data.get('name')}
Локация: {venue_data.get('address')}
Канал: {channel}
Стиль: {style}

Информация о MyTravel.kz:
- Топовая платформа бронирования туров в Казахстане
- 10,000+ активных туристов ежемесячно
- PMS система для управления бронированиями
- Продвижение для премиум объектов
- Рассрочка и страхование для туристов

Требования:
- Персонализация (упомяни название объекта и локацию)
- Подчеркни преимущества платформы
- Добавь CTA (call-to-action)
- Длина: 3-5 предложений
- Дружелюбный тон

Пиши на русском языке."""

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Outreach generation error: {e}")
            return self._get_fallback_template(venue_data, channel)

    def _get_fallback_template(self, venue_data: dict, channel: str) -> str:
        """Резервный шаблон если AI не сработал"""
        name = venue_data.get("name", "ваш объект")
        location = venue_data.get("address", "")

        return f"""Привет! 👋

Мы заметили ваш замечательный {name} в {location}.

MyTravel.kz — топовая платформа бронирования в Казахстане:
✅ 10,000+ туристов ежемесячно
✅ Удобная PMS система
✅ Рост бронирований

Хотим добавить вас в каталог. Обсудим? 

https://mytravel.kz/demo"""