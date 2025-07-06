from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dishka import FromDishka
from sqlmodel import Session

from bot.core.config import config
from bot.filters.admin import AdminFilter
from bot.services.user import change_user_admin_status

router = Router(name="upgrade_to_admin")


class SG(StatesGroup):
    admin_secret = State()
    promote_user = State()


@router.message(Command(commands="upgrade_to_admin"))
async def upgrade_to_admin(message: Message, state: FSMContext) -> None:
    await state.set_state(SG.admin_secret)
    await message.answer(f"Enter secret code")


@router.message(SG.admin_secret)
async def do_upgrade(
    message: Message, state: FSMContext, session: FromDishka[Session]
) -> None:
    await state.clear()
    if message.text == config.ADMIN_PASS:
        change_user_admin_status(
            session=session, user_id=message.from_user.id, admin=True
        )
        await message.answer("✅ Done")
    else:
        await message.answer("❌ Wrong secret")


@router.message(Command(commands="user_to_admin"), AdminFilter())
async def _(message: Message, state: FSMContext) -> None:
    await state.set_state(SG.promote_user)
    await message.reply(
        """
Send username. with admin status as number. Example:


    <b>username 1</b> - make user admin
    
    or 
    
    <b>username 0</b> - remove admin status
                        """
    )


@router.message(SG.promote_user)
async def _(message: Message, state: FSMContext, session: FromDishka[Session]) -> None:
    await state.clear()
    try:
        username, new_admin_status = message.text.split(" ")
        new_admin_status = True if new_admin_status == "1" else False
    except Exception as e:
        return await message.reply(str(e))

    change_user_admin_status(session=session, username=username, admin=new_admin_status)
    await message.answer("✅ Done")
