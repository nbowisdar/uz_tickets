from aiogram import types
from loguru import logger
from sqlalchemy import select
from sqlmodel import Session, update

from bot.models.user import User


def is_admin(session: Session, user_id: int) -> bool:
    """Checks if the user is an admin."""
    user = session.get(User, user_id)
    if user and user.is_admin:
        return True
    return False


def user_exists(session: Session, user_id: int) -> bool:
    """Checks if the user is in the database."""
    stm = select(User).where(User.id == user_id)
    result = session.exec(stm).all()
    return bool(result)


def add_user(
    session: Session,
    user: types.User,
    is_admin: bool = False,
    referrer: str | None = None,
) -> None:
    """Add a new user to the database."""
    logger.info(f"new user registration | user_id: {user.id} | username: {user.username}")
    new_user = User(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
        is_premium=user.is_premium or False,
        referrer=referrer,
        is_admin=is_admin,
    )

    session.add(new_user)
    session.commit()


def change_user_admin_status(
    session: Session,
    *,
    admin: bool,
    user_id: int | None = None,
    username: str | None = None,
):
    stmt = update(User)
    if user_id:
        stmt = stmt.where(User.id == user_id)
    elif username:
        stmt = stmt.where(User.username == username)
    else:
        raise Exception("Provide user_id or username")

    stmt = stmt.values(is_admin=admin)
    session.exec(stmt)
    session.commit()
