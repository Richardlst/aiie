from typing import Annotated
from fastapi import Depends

from app.service.face_refine import FaceRefineService
from app.dependencies.dependencies import StorageServiceDep


def get_face_refine_service(storage_service: StorageServiceDep) -> FaceRefineService:
    return FaceRefineService(storage_service)


FaceRefineServiceDep = Annotated[FaceRefineService, Depends(get_face_refine_service)]
