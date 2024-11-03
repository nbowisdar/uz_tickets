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
    DEBUG: bool = False
    MEDIA_GROUP_TIMEOUT: int = 1
    MAIN_CHANNEL_ID: int = -1002364057221
    CHILD_CHANNEL_IDS: list[str] = ["-1002174716776", "-1002288010761"]

    # Postgres
    POSTGRES_DSN: PostgresDsn
    # Redis
    REDIS_DSN: RedisDsn
    # RabbitMQ
    RABBITMQ_DSN: str


@lru_cache
def get_config() -> Config:
    return Config()
