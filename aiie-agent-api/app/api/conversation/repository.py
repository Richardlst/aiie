import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.repository import BaseRepository
from app.api.conversation.models import Conversation


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Conversation:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return (await self.session.exec(statement)).all()
