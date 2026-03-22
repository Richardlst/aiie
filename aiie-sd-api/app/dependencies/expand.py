from typing import Annotated
from fastapi import Depends

from app.service.expand import ExpandService
from app.dependencies.dependencies import StorageServiceDep


def get_expand_service(storage_service: StorageServiceDep) -> ExpandService:
    return ExpandService(storage_service)


ExpandServiceDep = Annotated[ExpandService, Depends(get_expand_service)]
