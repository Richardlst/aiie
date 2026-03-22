import json
import uuid
from typing import List
from io import BytesIO
from fastapi import UploadFile

from minio import Minio

from app.settings import settings
from app.models import UploadImage, UploadMultipleResponse, UploadResponse


class StorageService:
    def __init__(self, minio_client: Minio):
        self.minio_client = minio_client
        self._create_bucket()

    def _get_image_url(self, name: str) -> str:
        endpoint = settings.MINIO_RETURN_ENDPOINT
        if settings.MINIO_SECURE:
            return f"https://{endpoint}/images/{name}"
        return f"http://{endpoint}/images/{name}"

    def _create_bucket(self):
        if not self.minio_client.bucket_exists("images"):
            self.minio_client.make_bucket("images")

        # Set policy cho bucket là public-read
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": ["arn:aws:s3:::images/*"],
                }
            ],
        }
        self.minio_client.set_bucket_policy("images", json.dumps(policy))

    async def upload_image(self, file: UploadFile) -> UploadResponse:
        # Tạo unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Upload file
        file_data = await file.read()

        self.minio_client.put_object(
            "images",
            unique_filename,
            data=BytesIO(file_data),
            length=len(file_data),
            content_type=file.content_type,
        )

        # Reset file pointer để có thể đọc lại nếu cần
        await file.seek(0)

        # Trả về direct URL
        url = self._get_image_url(unique_filename)

        result = UploadImage(filename=unique_filename, url=url)
        return UploadResponse(data=result)

    async def upload_multiple_images(
        self, files: List[UploadFile]
    ) -> UploadMultipleResponse:
        uploaded_files = []
        for file in files:
            # Tạo unique filename
            file_extension = file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"

            # Upload file
            file_data = await file.read()
            self.minio_client.put_object(
                "images",
                unique_filename,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=file.content_type,
            )

            # Thêm thông tin file vào danh sách
            uploaded_files.append(
                {
                    "filename": unique_filename,
                    "url": self._get_image_url(unique_filename),
                }
            )

        result = [
            UploadImage(filename=file["filename"], url=file["url"])
            for file in uploaded_files
        ]
        return UploadMultipleResponse(data=result)

    async def delete_image(self, filename: str):
        self.minio_client.stat_object("images", filename)
        self.minio_client.remove_object("images", filename)
        return {"message": "Xóa file thành công", "filename": filename}
