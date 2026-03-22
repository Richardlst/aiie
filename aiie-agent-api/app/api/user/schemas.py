import uuid
from pydantic import BaseModel, Field
from typing import Optional
from app.api.user.models import UserBase
from datetime import datetime


class UserCreate(UserBase):
    password: str
    active: bool = False


class UserUpdate(BaseModel):
    password: Optional[str] = None
    active: Optional[bool] = None
    
class UserUpdatePub(BaseModel):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
