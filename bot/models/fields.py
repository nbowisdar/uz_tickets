from typing import Annotated
import uuid

from sqlalchemy import UUID, BigInteger, text
from sqlalchemy.orm import mapped_column


uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        server_default=text("gen_random_uuid()"),
    ),
]


chat_id_bigint = Annotated[int, mapped_column(BigInteger(), unique=True)]
