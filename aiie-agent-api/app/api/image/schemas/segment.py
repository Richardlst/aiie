from pydantic import BaseModel, Field


class SegmentRequest(BaseModel):
    image_url: str = Field(
        title="Image Url",
        description="URL of the image you want to segment. This is the image that will be analyzed to identify and separate specific objects or regions.",
    )
    prompts: str = Field(
        title="Prompts",
        description="Text prompts specifying what objects or regions to segment in the image. Multiple objects can be specified by separating with commas (e.g., 'cat, table, person').",
    )
