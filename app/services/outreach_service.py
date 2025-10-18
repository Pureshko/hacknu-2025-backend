from typing import Dict, Any


class OutreachService:
    def __init__(self):
        self.templates = {
            "luxury_glamping": self._luxury_glamping_template,
            "family_guest_house": self._family_guest_house_template,
            "eco_tourism": self._eco_tourism_template,
            "ethno_tourism": self._ethno_tourism_template,
            "mountain_house": self._mountain_house_template
        }
    
    def generate_outreach_message(
        self, 
        accommodation: Dict[str, Any],
        channel: str = "whatsapp"
    ) -> str:
        """Generate personalized outreach message"""
        
        acc_type = accommodation.get("accommodation_type", "")
        template_func = self.templates.get(
            acc_type, 
            self._default_template
        )
        
        return template_func(accommodation, channel)
    
    def _luxury_glamping_template(
        self, 
        acc: Dict, 
        channel: str
    ) -> str:
        """Template for luxury glamping"""
        
        name = acc.get("name", "")
        region = acc.get("region", "")
        
        return f"""Привет, {name}!

Мы заметили ваш потрясающий глэмпинг рядом с {region}. Ваше место явно заслуживает большей аудитории туристов!

mytravel.kz — это топовая платформа путешествий в Казахстане, где вы получите:
✅ 10К+ активных туристов ежемесячно
✅ Лучший рейтинг для премиум объектов
✅ Инструменты управления бронированиями
✅ Продвижение в соцсетях

Хотим добавить вас в каталог. Можно поговорить?

Демо-аккаунт: https://mytravel.kz/demo

С уважением,
Команда mytravel.kz"""
    
    def _family_guest_house_template(
        self, 
        acc: Dict, 
        channel: str
    ) -> str:
        """Template for family guest houses"""
        
        name = acc.get("name", "")
        region = acc.get("region", "")
        
        return f"""Здравствуйте, {name}!

Ваш гостевой дом в {region} идеально подходит для семейного отдыха!

mytravel.kz помогает семьям находить безопасные и комфортные места для отдыха в Казахстане.

Что мы предлагаем:
✅ Целевая аудитория: семьи с детьми
✅ Простая система бронирования
✅ Рассрочка для туристов (выше спрос)
✅ Туристическая страховка

Присоединяйтесь бесплатно: https://mytravel.kz/register

Команда mytravel.kz"""
    
    def _eco_tourism_template(
        self, 
        acc: Dict, 
        channel: str
    ) -> str:
        """Template for eco-tourism"""
        
        name = acc.get("name", "")
        region = acc.get("region", "")
        
        return f"""Привет, {name}!

Ваш эко-объект в {region} — это именно то, что ищут наши туристы!

Эко-туризм набирает популярность, и mytravel.kz — лучшая платформа для продвижения природного отдыха.

Преимущества:
🌿 Аудитория эко-туристов
🌿 Специальная категория на сайте
🌿 Продвижение уникальных мест Казахстана
🌿 Аналитика и отзывы

Давайте сотрудничать: https://mytravel.kz/eco

С уважением,
mytravel.kz"""
    
    def _ethno_tourism_template(
        self, 
        acc: Dict, 
        channel: str
    ) -> str:
        """Template for ethno-tourism"""
        
        name = acc.get("name", "")
        region = acc.get("region", "")
        
        return f"""Сәлем, {name}!

Ваша юрта в {region} — уникальный культурный опыт для туристов!

mytravel.kz продвигает казахстанское культурное наследие и аутентичный отдых.

Почему стоит присоединиться:
🏛 Специальная категория "Этно-туризм"
🏛 Иностранные и местные туристы
🏛 Популяризация традиций Казахстана
🏛 Поддержка местного бизнеса

Зарегистрируйтесь: https://mytravel.kz/ethno

Команда mytravel.kz"""
    
    def _mountain_house_template(
        self, 
        acc: Dict, 
        channel: str
    ) -> str:
        """Template for mountain houses"""
        
        name = acc.get("name", "")
        region = acc.get("region", "")
        
        return f"""Привет, {name}!

Ваш горный домик в {region} — мечта любителей приключений!

mytravel.kz — платформа для активного и приключенческого туризма в Казахстане.

Что вы получите:
⛰ Целевая аудитория: активные туристы
⛰ Продвижение горных маршрутов
⛰ Сезонные кампании
⛰ Партнерство с турагентствами

Начните привлекать туристов: https://mytravel.kz/mountain

С уважением,
mytravel.kz"""
    
    def _default_template(
        self, 
        acc: Dict, 
        channel: str
    ) -> str:
        """Default template"""
        
        name = acc.get("name", "")
        
        return f"""Здравствуйте, {name}!

Мы заметили ваш объект размещения на 2GIS и хотим предложить сотрудничество.

mytravel.kz — ведущая платформа для бронирования туров и размещения в Казахстане.

Преимущества партнерства:
✅ Тысячи активных туристов
✅ Бесплатная регистрация
✅ Удобная система управления
✅ Поддержка 24/7

Присоединяйтесь: https://mytravel.kz/partner

Команда mytravel.kz"""