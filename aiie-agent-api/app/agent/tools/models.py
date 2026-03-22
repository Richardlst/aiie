from pydantic import BaseModel, Field


class GenerationResponse(BaseModel):
    image_url: str = Field(description="URL to access the generated image")
