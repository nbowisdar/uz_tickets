import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.types import ErrorEvent
from aiogram_dialog import AccessSettings, DialogManager, StartMode, setup_dialogs
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from bot.config import get_config
from bot.dialogs.menu.dialog import menu_dialog
from bot.handlers.commands import commands_router
from bot.ioc import DepsProvider
from bot.misc import bot, dp
from bot.states import Menu
from bot.utils import setup_logging

config = get_config()
setup_logging(config)
logger = logging.getLogger(__name__)

main_router = Router()


def register_dialogs(router: Router):
    """
    Register all dialogs in the router
    """
    router.include_router(commands_router)
    router.include_router(menu_dialog)


@main_router.error()
async def error_handler(event: ErrorEvent, dialog_manager: DialogManager):
    logger.error("Error occurred: %s", event.exception, exc_info=event.exception)
    await dialog_manager.start(
        Menu.main,
        mode=StartMode.RESET_STACK,
        access_settings=AccessSettings(config.ADMIN_IDS),
    )


async def setup_dispatcher(dp: Dispatcher):
    logger.info("Admin IDs: %s", config.ADMIN_IDS)
    container = make_async_container(DepsProvider())
    setup_dishka(container=container, router=dp)
    dp.include_router(main_router)
    register_dialogs(dp)
    setup_dialogs(dp)


async def start_pooling():
    await setup_dispatcher(dp)
    await dp.start_polling(bot, skip_updates=True)


async def setup_webhook(bot: Bot):
    await setup_dispatcher(dp)
    await bot.set_webhook(config.WEBHOOK_URL, secret_token=config.BOT_SECRET_TOKEN)
