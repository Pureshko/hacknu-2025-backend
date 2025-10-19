from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
import secrets


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_ignore_empty": True,
        "extra": "ignore",
    }
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ALGORITHM: str = "HS256"
    
    # Environment
    ENVIRONMENT: str = "local"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return str(MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ))
    
    # API Keys
    TWOGIS_API_KEY: str
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # API URLs
    TWOGIS_PLACES_API: str = "https://catalog.api.2gis.com/3.0/items"
    TWOGIS_GEOCODER_API: str = "https://catalog.api.2gis.com/3.0/geocode"
    
    # Rate Limits
    TWOGIS_RATE_LIMIT: int = 600
    GOOGLE_RATE_LIMIT: int = 100
    
    # Application Settings
    ACCOMMODATION_CATEGORIES: List[str] = [
        "luxury_glamping",
        "family_guest_house",
        "eco_tourism",
        "ethno_tourism",
        "mountain_house"
    ]
    
    REGIONS: List[str] = ["Almaty"]


settings = Settings()