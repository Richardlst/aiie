import uuid
from enum import Enum as PyEnum
from sqlalchemy import VARCHAR, Text
from sqlmodel import Field, SQLModel

from app.core.models import BaseIDModel, BaseTimestampModel


class MessageRole(str, PyEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class MessageBase(SQLModel):
    model_config = {"arbitrary_types_allowed": True}

    content: str = Field(sa_type=Text)
    role: MessageRole = Field(
        sa_type=VARCHAR(10),
    )
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")


class Message(MessageBase, BaseIDModel, BaseTimestampModel, table=True):
    pass
