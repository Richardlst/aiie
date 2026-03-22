from typing import Optional
import uuid
from fastapi import HTTPException

from app.api.auth.schemas import TokenData
from app.api.conversation.models import Conversation
from app.api.conversation.repository import ConversationRepository
from app.api.conversation.schemas import ConversationUpdate
from app.core.logger import setup_logger

logger = setup_logger("ConversationService")


class ConversationService:
    def __init__(self, conversation_repository: ConversationRepository):
        self.conversation_repository = conversation_repository

    async def valid_conversation(
        self, conversation_id: uuid.UUID, token_data: TokenData
    ) -> Conversation:
        conversation = await self.get(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if str(conversation.user_id) != token_data.sub:
            raise HTTPException(status_code=403, detail="Forbidden")

        return conversation

    async def get_by_user_id(self, user_id: uuid.UUID) -> Conversation:
        return await self.conversation_repository.get_by_user_id(user_id)

    async def get(self, id: uuid.UUID) -> Optional[Conversation]:
        return await self.conversation_repository.find_by_id(id)

    async def create(self, token_data: TokenData) -> Conversation:
        return await self.conversation_repository.create(
            obj_in=Conversation(user_id=token_data.sub)
        )

    async def update(
        self, token_data: TokenData, id: uuid.UUID, input: ConversationUpdate
    ) -> Conversation:
        conversation = await self.valid_conversation(id, token_data)

        for key, value in input.model_dump(exclude_unset=True).items():
            setattr(conversation, key, value)

        return await self.conversation_repository.update(conversation)

    async def delete(self, token_data: TokenData, id: uuid.UUID) -> Conversation:
        conversation = await self.valid_conversation(id, token_data)

        return await self.conversation_repository.delete_by_obj(conversation)
