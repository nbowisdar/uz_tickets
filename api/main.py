import logging
from typing import Annotated
from aiogram.types import Update
from fastapi import FastAPI, Header
from starlette.middleware.cors import CORSMiddleware

from bot.config import get_config
from bot.main import dp, bot
from bot.utils import setup_logging

config = get_config()
setup_logging(config)
logger = logging.getLogger(__name__)

app = FastAPI(title=config.API_NAME)

origins = [
    "http://bot.arturboyun.com",
    "https://bot.arturboyun.com",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(config.WEBHOOK_PATH)
async def webhook(
    update: dict,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> None | dict:
    if x_telegram_bot_api_secret_token != config.BOT_SECRET_TOKEN:
        logger.error("Wrong secret token!")
        return {"status": "error", "message": "Wrong secret token !"}
    telegram_update = Update(**update)
    await dp.feed_webhook_update(bot=bot, update=telegram_update)
    return {"ok": True}
