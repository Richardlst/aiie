from app.core.dependencies import AsyncSessionDep
from app.api.conversation.repository import ConversationRepository
from app.api.conversation.service import ConversationService
from typing import Annotated
from fastapi import Depends


def get_conversation_repository(
    session: AsyncSessionDep,
):
    return ConversationRepository(session)


def get_conversation_service(
    conversation_repository: Annotated[
        ConversationRepository, Depends(get_conversation_repository)
    ],
):
    return ConversationService(conversation_repository)


ConversationServiceDep = Annotated[
    ConversationService, Depends(get_conversation_service)
]
