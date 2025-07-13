# Dispatcher
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.core.config import get_config

config = get_config()

key_builder = DefaultKeyBuilder(with_destiny=True)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Bot
default_bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=config.BOT_TOKEN, default=default_bot_properties)
