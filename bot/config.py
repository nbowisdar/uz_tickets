from functools import lru_cache
from typing import final

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_NAME = ".env"


@final
class Config(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(env_file=ENV_FILE_NAME)

    # Bot
    BOT_TOKEN: str
    ADMIN_IDS: list[int] = [
        123123,
    ]
    DEBUG: bool = True

    # Postgres
    POSTGRES_DSN: PostgresDsn
    # Redis
    REDIS_DSN: RedisDsn
    # RabbitMQ
    RABBITMQ_DSN: str


@lru_cache
def get_config() -> Config:
    return Config()
