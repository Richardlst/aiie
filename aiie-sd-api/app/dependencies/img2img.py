
from typing import Annotated
from fastapi import Depends

from app.service.img2img import Img2ImgService
from app.dependencies.dependencies import StorageServiceDep


def get_img2img_service(storage_service: StorageServiceDep) -> Img2ImgService:
    return Img2ImgService(storage_service)

Img2ImgServiceDep = Annotated[Img2ImgService, Depends(get_img2img_service)]
