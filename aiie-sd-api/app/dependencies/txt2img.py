from typing import Annotated
from fastapi import Depends

from app.service.txt2img import Txt2ImgService
from app.dependencies.dependencies import StorageServiceDep


def get_txt2img_service(storage_service: StorageServiceDep) -> Txt2ImgService:
    return Txt2ImgService(storage_service)


Txt2ImgServiceDep = Annotated[Txt2ImgService, Depends(get_txt2img_service)]
