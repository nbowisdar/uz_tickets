from contextlib import contextmanager
from typing import Generator

from loguru import logger
from sqlmodel import Session, create_engine

from src.bot.core.config import get_config

config = get_config()
engine = create_engine(str(config.POSTGRES_DSN), echo=config.DEBUG)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    sessino = Session(engine)
    try:
        logger.debug("Session created")
        yield sessino
    finally:
        logger.debug("Session closed")
        sessino.close()
