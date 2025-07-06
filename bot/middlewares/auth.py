# from __future__ import annotations

# from typing import TYPE_CHECKING, Any

# from aiogram import BaseMiddleware
# from aiogram.types import Message
# from loguru import logger

# from bot.core.config import config
# from bot.database.db import get_session
# from bot.services.user import add_user, user_exists
# from bot.utils.command import find_command_argument

# if TYPE_CHECKING:
#     from collections.abc import Awaitable, Callable

#     from aiogram.types import TelegramObject



# class AuthMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: dict[str, Any],
#     ) -> Any:
#         if not isinstance(event, Message):
#             return await handler(event, data)
#         message: Message = event
#         user = message.from_user
#         if not user:
#             return await handler(event, data)
#         with get_session() as session:

            


#             return await handler(event, data)