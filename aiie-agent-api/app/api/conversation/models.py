from typing import Optional
from sqlmodel import Field, SQLModel
import uuid
from sqlalchemy import VARCHAR
from app.core.models import BaseIDModel, BaseTimestampModel


class ConversationBase(SQLModel):
    model_config = {"arbitrary_types_allowed": True}

    name: Optional[str] = Field(sa_type=VARCHAR(255), nullable=True)


class Conversation(ConversationBase, BaseIDModel, BaseTimestampModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id")
