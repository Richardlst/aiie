# app/core/models.py
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import event, DateTime
import uuid


class BaseIDModel(SQLModel):
    __abstract__ = True

    id: uuid.UUID = Field(
        primary_key=True,
        unique=True,
        default_factory=uuid.uuid4,
    )


class BaseTimestampModel(SQLModel):
    __abstract__ = True

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=DateTime(timezone=True),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_type=DateTime(timezone=True),
    )


class BaseAuditModel(BaseTimestampModel):
    __abstract__ = True

    created_by: Optional[uuid.UUID] = Field(default=None, nullable=True)
    updated_by: Optional[uuid.UUID] = Field(default=None, nullable=True)


# Register an event listener for update events
@event.listens_for(BaseTimestampModel, "before_update", propagate=True)
def receive_before_update(mapper, connection, target: BaseTimestampModel):
    # Update updated_at to the current time
    target.updated_at = datetime.now(timezone.utc)
