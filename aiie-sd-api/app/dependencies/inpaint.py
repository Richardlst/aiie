from typing import Annotated
from fastapi import Depends

from app.service.inpaint import InpaintService
from app.dependencies.dependencies import StorageServiceDep


def get_inpaint_service(storage_service: StorageServiceDep) -> InpaintService:
    return InpaintService(storage_service)


InpaintServiceDep = Annotated[InpaintService, Depends(get_inpaint_service)]
