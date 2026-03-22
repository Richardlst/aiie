import uuid
from typing import Dict
from enum import Enum
from fastapi import WebSocket
from pydantic import BaseModel


WSConnections = Dict[uuid.UUID, Dict[str, WebSocket]]


class WSResponseType(str, Enum):
    PROCESSING = "processing"


class WSResponseDataProcessing(BaseModel):
    process_name: str


WSResponseData = WSResponseDataProcessing


class WSResponse(BaseModel):
    type: WSResponseType
    data: WSResponseData
