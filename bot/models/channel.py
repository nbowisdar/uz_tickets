from bot.models.base import Base, big_int_pk


class Channel(Base, table=True):
    id: big_int_pk
    name: str
    chat_id: int
