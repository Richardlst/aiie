from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import VARCHAR
from app.core.models import BaseIDModel, BaseTimestampModel


class UserBase(SQLModel):
    email: str = Field(unique=True, sa_type=VARCHAR(255))


class User(UserBase, BaseIDModel, BaseTimestampModel, table=True):
    password: Optional[str] = Field(
        max_length=255, default=None, nullable=True, sa_type=VARCHAR(255)
    )
    active: bool = Field(default=False)
