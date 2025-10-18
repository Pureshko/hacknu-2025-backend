from openai import AsyncOpenAI
from app.config import get_settings
from app.models import CategoryEnum

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class DescriptionGenerator:
    """Генератор AI-описаний для объектов"""

    async def generate_description(self, venue_data: dict) -> str:
        """Генерирует привлекательное описание объекта"""
        
        prompt = f"""Создай привлекательное описание для туристического объекта на платформе MyTravel.kz.

Объект: {venue_data.get('name')}
Категория: {venue_data.get('category')}
Адрес: {venue_data.get('address')}
Удобства: {', '.join(venue_data.get('amenities', []))}
Оригинальное описание: {venue_data.get('description', 'Не указано')}

Требования:
- Длина: 3-4 абзаца
- Подчеркни уникальность и преимущества
- Упомяни удобства
- Создай атмосферу и эмоциональную привлекательность
- Закончи призывом к бронированию
- Пиши на русском языке

Пример структуры:
1. Вступление (что это за место)
2. Описание условий и удобств
3. Уникальные особенности
4. Призыв к действию"""

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Description generation error: {e}")
            return self._get_fallback_description(venue_data)
    
    def _get_fallback_description(self, venue_data: dict) -> str:
        """Резервное описание если AI не сработал"""
        name = venue_data.get('name', 'объект')
        category = venue_data.get('category', 'туристический объект')
        
        return f"""Добро пожаловать в {name}!

Мы предлагаем комфортабельное размещение в категории {category}. 
Наш объект оборудован всем необходимым для приятного отдыха.

Забронируйте проживание через MyTravel.kz и получите лучшие условия!"""


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