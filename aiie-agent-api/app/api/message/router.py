import uuid
from typing import List

from fastapi import APIRouter

from app.api.auth.dependencies import AuthenticateDep
from app.api.message.dependencies import MessageServiceDep
from app.api.message.schemas import (
    AddMessageRequest,
    AddMessageResponse,
    MessageResponse,
)

router = APIRouter(prefix="/message", tags=["message"])


@router.get("/{conversation_id}", response_model=List[MessageResponse])
async def get_messages(
    service: MessageServiceDep,
    conversation_id: uuid.UUID,
    token_data: AuthenticateDep,
):
    return await service.get_by_conversation_id(conversation_id, token_data)


@router.post("", response_model=AddMessageResponse)
async def add_message(
    service: MessageServiceDep,
    token_data: AuthenticateDep,
    request: AddMessageRequest,
):
    return await service.add_message(token_data, request)
