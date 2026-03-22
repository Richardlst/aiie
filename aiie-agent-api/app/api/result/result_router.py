from typing import Annotated
from fastapi import APIRouter, Query

from app.api.auth.dependencies import AuthenticateDep
from app.api.result.dependencies.get_result_base_service import ResultBaseServiceDep
from app.api.result.schemas.result_response import ResultResponse
from app.core.schemas import PagingRequest, PagingResponse


result_router = APIRouter(prefix="/result", tags=["result"])


@result_router.get("/paging", response_model=PagingResponse[ResultResponse])
async def paginate_results(
    result_base_service: ResultBaseServiceDep,
    token_data: AuthenticateDep,
    request: Annotated[PagingRequest, Query()],
):
    return await result_base_service.paginate_by_user_id(
        user_id=token_data.sub, request=request
    )
