import uuid

from sqlalchemy import func
from sqlmodel import select
from app.api.result.models.result import Result
from app.core.repository import BaseRepository
from app.core.schemas import PagingRequest, PagingResponse


class ResultRepository(BaseRepository[Result]):
    def __init__(self, session):
        super().__init__(Result, session)
        
    async def paginate_by_user_id(
        self, user_id: uuid.UUID, request: PagingRequest
    ) -> PagingResponse[Result]:
        statement = (
            select(Result)
            .where(Result.user_id == user_id)
            .order_by(
                Result.updated_at.desc().nulls_last(),
                Result.created_at.desc(),
            )
        )
        total = await self.session.scalar(select(func.count()).select_from(statement))
        total_pages = (total + request.page_size - 1) // request.page_size
        scalar = await self.session.exec(
            statement.offset((request.page - 1) * request.page_size).limit(
                request.page_size
            )
        )
        result = scalar.all()
        return PagingResponse(
            data=result,
            page=request.page,
            page_size=request.page_size,
            total=total,
            total_pages=total_pages,
        )