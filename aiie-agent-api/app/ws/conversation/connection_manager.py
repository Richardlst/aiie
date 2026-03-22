import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.logger import setup_logger
from .schemas import WSConnections, WSResponse

logger = setup_logger("ConnectionManager")


class ConnectionManager:
    def __init__(self, connections: WSConnections):
        self.connections = connections

    async def connect(self, conversation_id: uuid.UUID, websocket: WebSocket):
        if conversation_id not in self.connections:
            self.connections[conversation_id] = {}

        session_id = str(uuid.uuid4())
        self.connections[conversation_id][session_id] = websocket
        return session_id

    def disconnect(self, conversation_id: uuid.UUID, session_id: str):
        if conversation_id in self.connections:
            if session_id in self.connections[conversation_id]:
                del self.connections[conversation_id][session_id]

            if not self.connections[conversation_id]:
                del self.connections[conversation_id]

    async def send(self, conversation_id: uuid.UUID, response: WSResponse):
        if conversation_id in self.connections:
            disconnected_sessions = []

            for session_id, websocket in self.connections[conversation_id].items():
                try:
                    if (
                        websocket.client_state == WebSocketState.CONNECTED 
                        and websocket.application_state == WebSocketState.CONNECTED
                    ):
                        await websocket.send_json(response.model_dump(mode="json"))
                    else:
                        logger.warning(
                            f"WebSocket for session {session_id} is not fully connected. Client state: {websocket.client_state}, App state: {websocket.application_state}"
                        )
                        disconnected_sessions.append(session_id)
                except Exception as e:
                    logger.error(
                        f"Error sending message to session {session_id}: {str(e)}"
                    )
                    disconnected_sessions.append(session_id)

            # Clean up disconnected sessions
            for session_id in disconnected_sessions:
                self.disconnect(conversation_id=conversation_id, session_id=session_id)
