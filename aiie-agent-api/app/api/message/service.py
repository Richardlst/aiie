import uuid
from typing import List
from langchain_core.prompts import ChatPromptTemplate

from app.agent.agent import Agent
from app.agent.state import State
from app.api.conversation.schemas import ConversationUpdate
from app.api.conversation.service import ConversationService
from app.api.message.schemas import (
    AddMessageRequest,
    AddMessageResponse,
    MessageCreate,
)
from app.api.auth.schemas import TokenData

from .models import Message, MessageRole
from .repository import MessageRepository


class MessageService:
    def __init__(
        self,
        repository: MessageRepository,
        conversation_service: ConversationService,
        agent: Agent,
    ):
        self.repository = repository
        self.__con_service = conversation_service
        self.__agent = agent

    async def __create_multiple(self, input: List[MessageCreate]) -> List[Message]:
        messages = await self.repository.create_multiple(
            obj_in=[Message(**message.model_dump()) for message in input]
        )
        return messages

    def __convert_message(
        self, messages: List[Message], request: AddMessageRequest
    ) -> List[Message]:
        messages = ChatPromptTemplate(
            messages=[
                (
                    message.role.lower(),
                    message.content,
                )
                for message in messages
            ]
            + [
                (
                    MessageRole.USER.lower(),
                    request.content,
                )
            ]
        ).format_messages()
        return messages

    async def add_message(
        self, token_data: TokenData, request: AddMessageRequest
    ) -> AddMessageResponse:
        # Get conversation and messages
        conversation = await self.__con_service.valid_conversation(
            request.conversation_id, token_data
        )
        messages = await self.get_by_conversation_id(
            token_data=token_data, conversation_id=conversation.id
        )
        messages = self.__convert_message(messages, request)

        # Call agent
        state: State = {
            "messages": messages,
            "conversation": conversation,
        }
        state = await self.__agent.ainvoke(state)

        # Create conversation if not exists
        if not conversation.name:
            con_name = state["conversation"].name

            conversation = await self.__con_service.update(
                token_data=token_data,
                id=conversation.id,
                input=ConversationUpdate(name=con_name),
            )

        # Create message
        res_content = state["messages"][-1].content
        messages = await self.__create_multiple(
            [
                MessageCreate(
                    content=request.content,
                    role=MessageRole.USER,
                    conversation_id=conversation.id,
                ),
                MessageCreate(
                    content=res_content,
                    role=MessageRole.ASSISTANT,
                    conversation_id=conversation.id,
                ),
            ]
        )

        result = AddMessageResponse(
            messages=messages,
            conversation=conversation,
        )

        return result

    async def get_by_conversation_id(
        self, conversation_id: uuid.UUID, token_data: TokenData
    ) -> List[Message]:
        await self.__con_service.valid_conversation(conversation_id, token_data)

        result = await self.repository.get_by_conversation_id(conversation_id)
        return result
