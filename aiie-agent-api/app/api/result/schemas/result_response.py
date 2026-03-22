from datetime import datetime
from typing import Optional
import uuid
from app.api.result.models.result_base import ResultBase


class ResultResponse(ResultBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
