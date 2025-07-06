from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.database.db import get_session
from bot.services.user import is_admin


class AdminFilter(BaseFilter):
    """Allows only administrators (whose database column is_admin=True)."""

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        with get_session() as session:
            user_id = message.from_user.id
            return is_admin(session=session, user_id=user_id)
