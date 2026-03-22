import uuid

from sqlmodel import Field
from app.api.result.models.result_base import ResultBase
from app.core.models import BaseIDModel, BaseTimestampModel


class Result(ResultBase, BaseIDModel, BaseTimestampModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id")
