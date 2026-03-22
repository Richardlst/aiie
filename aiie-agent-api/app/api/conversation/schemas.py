import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.conversation.models import ConversationBase


class ConversationResponse(ConversationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]


class ConversationUpdate(BaseModel):
    name: str = Field(default=None, description="The name of the conversation")
