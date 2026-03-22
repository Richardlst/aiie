from fastapi import APIRouter, UploadFile, File
from typing import List

from .models import UploadMultipleResponse, UploadResponse
from .dependencies import StorageServiceDep


router = APIRouter(prefix="/upload", tags=["storage"])


@router.post("", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    service: StorageServiceDep = None,
):
    return await service.upload_image(file)


@router.post("/multiple", response_model=UploadMultipleResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    service: StorageServiceDep = None,
):
    return await service.upload_multiple_images(files)


@router.delete("/delete/{filename}")
async def delete_image(
    filename: str,
    service: StorageServiceDep = None,
):
    return await service.delete_image(filename)
