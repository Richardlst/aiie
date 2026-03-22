from pydantic import BaseModel, Field


class SrRequest(BaseModel):
    image_url: str = Field(
        title="Image Url",
        description="URL of the image you want to upscale (super resolution).",
    )