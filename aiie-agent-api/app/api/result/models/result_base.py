from sqlalchemy import VARCHAR, Text
from sqlmodel import Field, SQLModel

from app.api.result.schemas.result_type import ResultType


class ResultBase(SQLModel):
    model_config = {"arbitrary_types_allowed": True}

    url: str = Field(sa_type=Text)
    type: ResultType = Field(sa_type=VARCHAR(3))
