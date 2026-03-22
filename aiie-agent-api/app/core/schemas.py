from pydantic import BaseModel
from typing import Any, Generic, Optional, Sequence, TypeVar
from sqlmodel import Field


class DataResponse(BaseModel):
    message: str
    data: Any


# Generic type for pagination
T = TypeVar("T")


class PagingRequest(BaseModel):
    """Parameters for pagination"""

    page: Optional[int] = Field(1, gt=0, description="Page number, starting from 1")
    page_size: Optional[int] = Field(
        10, gt=0, le=100, description="Number of items per page"
    )


class PagingResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    data: Sequence[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")