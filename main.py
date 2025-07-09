import asyncio

import uvicorn
from loguru import logger

from src.api import app
from src.bot.core.config import get_config
from src.bot.main import start_pooling
from src.bot.utils import setup_logging

config = get_config()
setup_logging(config)


if __name__ == "__main__":
    if config.USE_WEBHOOK:
        logger.info("Starting webhook server")

        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        logger.info("Starting bot polling")

        asyncio.run(start_pooling())
