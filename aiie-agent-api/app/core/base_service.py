from typing import Generic, TypeVar, Optional, List
import uuid
from sqlmodel import SQLModel

from app.core.repository import BaseRepository
from app.core.schemas import PagingRequest, PagingResponse

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseService(Generic[ModelType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    async def find_by_id_(self, id: uuid.UUID) -> Optional[ModelType]:
        return await self.repository.find_by_id(id)

    async def find_(self) -> List[ModelType]:
        return await self.repository.find()

    async def paginate_(self, request: PagingRequest) -> PagingResponse[ModelType]:
        return await self.repository.paginate(request=request)

    async def create_(self, obj_in: ModelType) -> ModelType:
        return await self.repository.create(obj_in)

    async def create_multiple_(self, obj_in: List[ModelType]) -> List[ModelType]:
        return await self.repository.create_multiple(obj_in)

    async def update_(self, obj_in: ModelType) -> ModelType:
        return await self.repository.update(obj_in)

    async def delete_(self, obj: ModelType):
        await self.repository.delete(obj)

    async def delete_by_id_(self, id: uuid.UUID):
        await self.repository.delete_by_id(id)

    async def delete_by_ids_(self, ids: list[uuid.UUID]) -> None:
        await self.repository.delete_by_ids(ids)

    async def delete_batch_(self, condition):
        await self.repository.delete_batch(condition)
