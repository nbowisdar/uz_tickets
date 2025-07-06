from typing import Iterable

from aiogram.types import TelegramObject
from dishka import Provider, Scope, provide
from loguru import logger
from sqlmodel import Session

from bot.core.config import config
from bot.database.db import get_session
from bot.services.user import add_user, user_exists
from bot.utils.command import find_command_argument

# @dataclass
# class Types:
# DBSession = Generator[Session, None, None]
# DBSession = Iterable[int]
DBSession = Iterable[Session]


def check_user(session, user, text):
    if user_exists(session, user.id):
        return
    referrer = find_command_argument(text)
    logger.info(f"new user registration | user_id: {user.id} | message: {text}")
    is_admin = False
    if user.id in config.ADMIN_IDS:
        is_admin = True
    add_user(session=session, user=user, referrer=referrer, is_admin=is_admin)


class DepsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self, obj: TelegramObject) -> Iterable[Session]:
        with get_session() as session:
            check_user(session, obj.from_user, obj.text)
            yield session
            # session will be closed in get_session generator

    @provide(scope=Scope.REQUEST)
    async def get_foo(self) -> str:
        return "bar"
