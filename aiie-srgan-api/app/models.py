from pydantic import BaseModel


class UploadImage(BaseModel):
    filename: str
    url: str


class UploadResponse(BaseModel):
    data: UploadImage
    
    
class UpscaleRequest(BaseModel):
    image_url: str
    
class UpscaleResponse(BaseModel):
    image_url: str
