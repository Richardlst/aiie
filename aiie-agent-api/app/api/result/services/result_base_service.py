import uuid
from app.api.result.models.result import Result
from app.api.result.result_repository import ResultRepository
from app.core.base_service import BaseService
from app.core.schemas import PagingRequest


class ResultBaseService(BaseService[Result]):
    def __init__(self, repository: ResultRepository):
        self.repository = repository

    async def paginate_by_user_id(self, user_id: uuid.UUID, request: PagingRequest):
        return await self.repository.paginate_by_user_id(user_id, request)
