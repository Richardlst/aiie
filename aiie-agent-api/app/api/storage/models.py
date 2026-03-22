from pydantic import BaseModel


class UploadImage(BaseModel):
    filename: str
    url: str


class UploadResponse(BaseModel):
    data: UploadImage


class UploadMultipleResponse(BaseModel):
    data: list[UploadImage]
