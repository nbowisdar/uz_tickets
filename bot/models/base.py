from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class Base(SQLModel):
    created_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)
    last_edited: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


big_int_pk = Annotated[int, Field(None, primary_key=True, sa_type=BigInteger)]
