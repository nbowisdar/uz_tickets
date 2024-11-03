from sqlalchemy.orm import Mapped
from bot.models.base import Base
from bot.models.fields import uuid_pk, chat_id_bigint


class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[uuid_pk]
    name: Mapped[str]
    chat_id: Mapped[chat_id_bigint]
