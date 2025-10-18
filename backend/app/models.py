from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    JSON,
    DateTime,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class CategoryEnum(str, enum.Enum):
    LUXURY_GLAMPING = "luxury_glamping"
    FAMILY_GUESTHOUSE = "family_guesthouse"
    ECOTOURISM = "ecotourism"
    ETHNO_TOURISM = "ethno_tourism"
    MOUNTAIN_HOUSE = "mountain_house"


class LeadStatus(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)

    # Основная информация
    name = Column(String, nullable=False)
    category = Column(Enum(CategoryEnum))
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)

    # Контакты
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    instagram = Column(String)
    telegram = Column(String)

    # Детали
    description = Column(String)
    rooms_count = Column(Integer)
    price_min = Column(Integer)
    price_max = Column(Integer)
    amenities = Column(JSON)  # ["wifi", "parking", "kitchen"]
    photos = Column(JSON)  # ["url1", "url2"]
    reviews_count = Column(Integer)
    rating = Column(Float)

    # AI-генерация
    ai_description = Column(String)
    ai_outreach_message = Column(String)

    # Скоринг
    score = Column(Float)  # 1-10
    lead_status = Column(Enum(LeadStatus))

    # Метаданные
    source = Column(String)  # "2gis", "google_maps"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)