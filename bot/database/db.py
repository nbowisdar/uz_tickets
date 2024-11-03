from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import get_config

config = get_config()
engine = create_async_engine(str(config.POSTGRES_DSN), echo=config.DEBUG)
SessionFactory = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)
