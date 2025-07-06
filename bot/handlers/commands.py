from typing import Iterable
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import AccessSettings, DialogManager, StartMode
from dishka import FromDishka
from loguru import logger
from sqlmodel import Session

from bot.core.config import get_config
from bot.ioc import DBSession
from bot.states import Menu

config = get_config()
commands_router = Router()


@commands_router.message(CommandStart())
async def command_start_handler(
    message: Message, dialog_manager: DialogManager
) -> None:
    logger.info(f"Command /start from {message.from_user.id}")  # type: ignore
    await dialog_manager.start(
        Menu.main,
        mode=StartMode.RESET_STACK,
        access_settings=AccessSettings(config.ADMIN_IDS),
    )


@commands_router.message(Command("foo"))
async def foo(message: Message, foo: FromDishka[str]) -> None:
    await message.answer(foo)


@commands_router.message(Command("db"))
async def test(message: Message, session: FromDishka[Iterable[Session]]) -> None:
    await message.answer("ok")
