from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import AccessSettings, DialogManager, StartMode
from dishka import FromDishka
from loguru import logger
from sqlmodel import Session

from bot.core.config import get_config
from bot.states import Menu

config = get_config()
router = Router()


@router.message(CommandStart())
async def command_start_handler(
    message: Message, dialog_manager: DialogManager
) -> None:
    logger.info(f"Command /start from {message.from_user.id}")  # type: ignore
    await dialog_manager.start(
        Menu.main,
        mode=StartMode.RESET_STACK,
        access_settings=AccessSettings(config.ADMIN_IDS),
    )


class SG(StatesGroup):
    order = State()


@router.message(Command("new_order"))
async def _(message: Message, state: FSMContext, session: FromDishka[Session]) -> None:
    print("Do smth")
    await state.set_state(SG.order)
    await message.answer("ok")


@router.message(SG.order)
async def _(message: Message, state: FSMContext, session: FromDishka[Session]) -> None:
    print("Do smth")

    await state.clear()
    await message.answer("ok")
