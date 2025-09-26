import secrets
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from pydantic import (
    EmailStr,
    PostgresDsn,
    computed_field,
)



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # BACKEND_CORS_ORIGINS: Annotated[
    #     list[AnyUrl] | str, BeforeValidator(parse_cors)
    # ] = []
    #
    # @computed_field  # type: ignore[prop-decorator]
    # @property
    # def all_cors_origins(self) -> list[str]:
    #     return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
    POSTGRES_SERVER: str
    POSTGRES_PORT: int 
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    ALGORITHM: str
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )  #         self.FRONTEND_HOST

settings = Settings()  # type: ignore