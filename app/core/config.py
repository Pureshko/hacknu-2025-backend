from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    TWOGIS_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # API URLs
    TWOGIS_PLACES_API: str = "https://catalog.api.2gis.com/3.0/items"
    TWOGIS_GEOCODER_API: str = "https://catalog.api.2gis.com/3.0/geocode"
    
    # Rate limits
    TWOGIS_RATE_LIMIT: int = 600  # per minute
    
    # Categories
    ACCOMMODATION_CATEGORIES: list = [
        "glamping",
        "guest_house",
        "yurt",
        "eco_cottage",
        "mountain_house"
    ]
    
    # Regions
    REGIONS: list = [
        "Almaty",
        "Astana",
        "Karaganda",
        "Shymkent",
        "Aktau"
    ]
    
    class Config:
        env_file = ".env"


settings = Settings()