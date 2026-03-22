from typing import Annotated
from fastapi import Depends

from app.service.colorize import ColorizeService
from app.dependencies.dependencies import StorageServiceDep


def get_colorize_service(storage_service: StorageServiceDep) -> ColorizeService:
    return ColorizeService(storage_service)


ColorizeServiceDep = Annotated[ColorizeService, Depends(get_colorize_service)]
