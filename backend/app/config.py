from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Config
    API_TITLE: str = "MyTravel AI Parser API"
    API_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # 2GIS
    GIS2_API_KEY: str
    
    GOOGLE_MAPS_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()