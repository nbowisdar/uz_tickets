from functools import lru_cache
from typing import final

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_NAME = ".env"


@final
class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE_NAME)

    # Bot
    BOT_TOKEN: str
    ADMIN_IDS: list[int] = [
        123123,
    ]
    DEBUG: bool = False
    USE_WEBHOOK: bool = False
    BOT_SECRET_TOKEN: str | None = None

    # API
    API_NAME: str = "Telegram Bot API"
    API_V1_STR: str = "/api/v1"
    API_HOST: str
    API_PORT: int | None = None
    ORIGINS: list[str] = [
        "http://bot.arturboyun.com",
        "https://bot.arturboyun.com",
        "http://localhost",
        "http://localhost:8000",
    ]

    # Postgres
    POSTGRES_DSN: PostgresDsn
    # Redis
    REDIS_DSN: RedisDsn

    @property
    def WEBHOOK_PATH(self) -> str:
        return f"{self.API_V1_STR}/webhook"

    @property
    def WEBHOOK_URL(self) -> str:
        return f"{self.API_HOST}{self.WEBHOOK_PATH}"


@lru_cache
def get_config() -> Config:
    return Config()  # type: ignore
