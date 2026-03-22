from typing import Annotated

from fastapi import Depends
from app.api.result.result_repository import ResultRepository
from app.core.dependencies import AsyncSessionDep


def get_result_repository(
    session: AsyncSessionDep,
):
    return ResultRepository(session)


ResultRepositoryDep = Annotated[ResultRepository, Depends(get_result_repository)]
