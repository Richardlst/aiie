from typing import Annotated

from fastapi import Depends

from app.agent.dependencies import AgentDep
from app.api.conversation.dependencies import ConversationServiceDep
from app.api.message.repository import MessageRepository
from app.api.message.service import MessageService
from app.core.dependencies import AsyncSessionDep


def get_message_repository(session: AsyncSessionDep) -> MessageRepository:
    return MessageRepository(session)


def get_message_service(
    agent: AgentDep,
    conversation_service: ConversationServiceDep,
    repository: MessageRepository = Depends(get_message_repository),
) -> MessageService:
    return MessageService(
        repository=repository,
        conversation_service=conversation_service,
        agent=agent,
    )


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
