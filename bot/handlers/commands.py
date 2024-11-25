import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import AccessSettings, DialogManager, StartMode

from bot.config import get_config
from bot.states import Menu

logger = logging.getLogger(__name__)

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


@commands_router.message(Command("photo_id"))
async def photo_id(message: Message):
    if not message.reply_to_message:
        return await message.answer("Reply to a photo message with this command.")
    logger.info(f"Command /photo_id from {message.from_user.id}")  # type: ignore
    await message.answer(
        f"Photo id: <code>{message.reply_to_message.photo[-1].file_id}</code>"  # type: ignore
    )
