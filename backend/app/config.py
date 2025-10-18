from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    

@lru_cache()
def get_settings():
    return Settings()