import asyncio
import time
import uuid

from fastapi import APIRouter, Body, Path, WebSocket, WebSocketDisconnect
from typing import List

from app.api.conversation.dependencies import ConversationServiceDep
from app.api.auth.dependencies import AuthenticateDep, AuthenticateWebsocketDep
from app.api.conversation.schemas import ConversationResponse, ConversationUpdate
from app.ws.conversation.dependencies import ConnectionManagerDep
from app.core.logger import setup_logger

router = APIRouter(prefix="/conversation", tags=["conversation"])

logger = setup_logger("ConversationRouter")


@router.get("", response_model=List[ConversationResponse])
async def get_conversations(
    conversation_service: ConversationServiceDep,
    token_data: AuthenticateDep,
):
    return await conversation_service.get_by_user_id(token_data.sub)


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation_service: ConversationServiceDep,
    token_data: AuthenticateDep,
):
    return await conversation_service.create(token_data)


@router.put("/{id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_service: ConversationServiceDep,
    token_data: AuthenticateDep,
    id: uuid.UUID = Path(..., description="The ID of the conversation to update"),
    input: ConversationUpdate = Body(..., description="The updated conversation"),
):
    return await conversation_service.update(token_data, id, input)


@router.delete("/{id}", response_model=ConversationResponse)
async def delete_conversation(
    conversation_service: ConversationServiceDep,
    token_data: AuthenticateDep,
    id: uuid.UUID = Path(..., description="The ID of the conversation to delete"),
):
    return await conversation_service.delete(token_data, id)


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: uuid.UUID,
    connection_manager: ConnectionManagerDep,
    _: AuthenticateWebsocketDep,
):
    await websocket.accept()

    logger.info(
        f"WebSocket connected: conversation_id: {conversation_id}, client: {websocket.client}"
    )

    session_id = await connection_manager.connect(
        conversation_id=conversation_id, websocket=websocket
    )
    
    ping_interval = 20  # seconds
    last_ping_time = time.time()
    
    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=5)
                if message == "pong":
                    logger.debug(f"Received pong from session {session_id}")
                    continue
                
            except asyncio.TimeoutError:
                current_time = time.time()
                if current_time - last_ping_time >= ping_interval:
                    try:
                        await websocket.send_text("ping")
                        last_ping_time = current_time
                        logger.debug(f"Sent ping to session {session_id}")
                    except Exception as e:
                        logger.error(f"Error sending ping to session {session_id}: {str(e)}")
                        raise WebSocketDisconnect()
                        
    except WebSocketDisconnect:
        logger.info(
            f"WebSocket disconnected: session_id: {session_id}, conversation_id: {conversation_id}"
        )
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        connection_manager.disconnect(
            conversation_id=conversation_id, session_id=session_id
        )
