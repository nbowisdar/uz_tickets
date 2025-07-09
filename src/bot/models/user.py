from typing import Literal

from sqlmodel import Field, Relationship

from .base import Base, big_int_pk

status: Literal["pending", "success", "error", "cancelled"]


class User(Base, table=True):
    id: big_int_pk

    username: str | None = Field(nullable=True, unique=True)
    first_name: str
    last_name: str | None
    balance: int = 0
    language_code: str | None = None
    referrer: str | None = None

    is_admin: bool = False
    is_suspicious: bool = False
    is_block: bool = False
    is_premium: bool = False

    orders: list["Order"] = Relationship(back_populates="user")


class Order(Base, table=True):
    id: big_int_pk
    train: str
    max_price: int  # 400_00 - penny

    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="orders")
    status: str = "pending"
