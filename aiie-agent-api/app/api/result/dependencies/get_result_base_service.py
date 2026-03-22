from typing import Annotated

from fastapi import Depends
from app.api.result.dependencies.get_result_repository import ResultRepositoryDep
from app.api.result.services.result_base_service import ResultBaseService


def get_result_base_service(
    repository: ResultRepositoryDep,
):
    return ResultBaseService(repository=repository)

ResultBaseServiceDep = Annotated[ResultBaseService, Depends(get_result_base_service)]
