from typing import List, Optional
import uuid
from datetime import datetime

from pydantic import BaseModel

from app.api.conversation.schemas import ConversationResponse
from app.api.message.models import MessageBase


class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]


class AddMessageRequest(BaseModel):
    content: str
    conversation_id: uuid.UUID
    files: Optional[List[str]] = None


class AddMessageResponse(BaseModel):
    messages: list[MessageResponse]
    conversation: ConversationResponse
