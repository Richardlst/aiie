from typing import Annotated
from fastapi import Depends
from minio import Minio

from app.core.settings import settings
from app.api.storage.service import StorageService


def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


MinioClientDep = Annotated[Minio, Depends(get_minio_client)]


def get_storage_service(minio_client: MinioClientDep = None) -> StorageService:
    return StorageService(minio_client)


StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]
