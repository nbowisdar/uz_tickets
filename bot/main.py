from aiogram import Bot, Dispatcher, Router
from aiogram.types import ErrorEvent
from aiogram_dialog import AccessSettings, DialogManager, StartMode, setup_dialogs
from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider, setup_dishka
from loguru import logger

from bot.core.config import get_config
from bot.dialogs.menu.dialog import menu_dialog
from bot.handlers import get_handlers_router
from bot.ioc import DepsProvider
from bot.middlewares import register_middlewares
from bot.misc import bot, dp
from bot.states import Menu
from bot.utils import setup_logging

config = get_config()
setup_logging(config)


main_router = Router()


def register_dialogs(router: Router):
    """
    Register all dialogs in the router
    """
    dp.include_router(get_handlers_router())
    router.include_router(menu_dialog)


@main_router.error()
async def error_handler(event: ErrorEvent, dialog_manager: DialogManager):
    logger.exception("Error occurred: {event.exception}")
    await dialog_manager.start(
        Menu.main,
        mode=StartMode.RESET_STACK,
        access_settings=AccessSettings(config.ADMIN_IDS),
    )


async def setup_dispatcher(dp: Dispatcher):
    logger.info(f"Admin IDs: {config.ADMIN_IDS}")
    container = make_async_container(DepsProvider(), AiogramProvider())
    setup_dishka(container=container, router=dp, auto_inject=True)
    dp.include_router(main_router)
    register_dialogs(dp)
    setup_dialogs(dp)
    register_middlewares(dp)


async def start_pooling():
    await setup_dispatcher(dp)
    await dp.start_polling(bot, skip_updates=True)


async def setup_webhook(bot: Bot):
    await setup_dispatcher(dp)
    await bot.set_webhook(config.WEBHOOK_URL, secret_token=config.BOT_SECRET_TOKEN)
