from typing import Generic, TypeVar, Type, Optional, List
import uuid
from sqlalchemy import func
from sqlmodel import SQLModel, select, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.schemas import PagingRequest, PagingResponse

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def find_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        detail = await self.session.get(self.model, id)
        return detail

    async def find(self) -> List[ModelType]:
        return await self.session.exec(select(self.model))

    async def paginate(self, request: PagingRequest) -> PagingResponse[ModelType]:
        statement = select(self.model)
        total = await self.session.scalar(select(func.count()).select_from(statement))
        total_pages = (total + request.page_size - 1) // request.page_size

        result = self.session.exec(
            statement.offset((request.page - 1) * request.page_size).limit(
                request.page_size
            )
        )

        return PagingResponse(
            data=result,
            page=request.page,
            page_size=request.page_size,
            total=total,
            total_pages=total_pages,
        )

    async def create(self, obj_in: ModelType) -> ModelType:
        self.session.add(obj_in)
        return obj_in

    async def create_multiple(self, obj_in: List[ModelType]) -> List[ModelType]:
        self.session.add_all(obj_in)
        return obj_in

    async def update(self, obj_in: ModelType) -> ModelType:
        return await self.session.merge(obj_in)

    async def delete(self, obj: ModelType):
        await self.session.delete(obj)

    async def delete_by_id(self, id: uuid.UUID):
        obj = await self.find_by_id(id)
        await self.session.delete(obj)

    async def delete_by_ids(self, ids: list[uuid.UUID]) -> None:
        statement = delete(self.model).where(self.model.id.in_(ids))
        await self.session.exec(statement)

    async def delete_batch(self, condition):
        statement = delete(self.model).where(condition)
        await self.session.exec(statement)
