from aiogram.filters import BaseFilter
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject
from sqlmodel import Session

from src.bot.services.user import is_admin


class AdminFilter(BaseFilter):
    """Allows only administrators (whose database column is_admin=True)."""

    @inject
    async def __call__(self, message: Message, session: FromDishka[Session]) -> bool:
        if not message.from_user:
            return False
        user_id = message.from_user.id
        return is_admin(session=session, user_id=user_id)
