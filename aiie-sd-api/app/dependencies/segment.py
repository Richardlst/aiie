from typing import Annotated
from fastapi import Depends

from app.service.segment import SegmentationService
from app.dependencies.dependencies import StorageServiceDep


def get_segmentation_service(storage_service: StorageServiceDep) -> SegmentationService:
    return SegmentationService(storage_service)


SegmentationServiceDep = Annotated[
    SegmentationService, Depends(get_segmentation_service)
]
