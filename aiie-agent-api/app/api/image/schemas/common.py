from pydantic import BaseModel, Field
from typing import Literal
    
SDModel = Literal[
    "runwayml/stable-diffusion-v1-5",
    "dreamlike-art/dreamlike-photoreal-2.0",
    "nitrosocke/mo-di-diffusion",
    "nitrosocke/Ghibli-Diffusion",
    "stablediffusionapi/disney-pixal-cartoon"
]


ExpandModel = Literal["runwayml/stable-diffusion-inpainting"]





class GenerationResponse(BaseModel):
    image_url: str = Field(
        title="Image Url",
        description="URL to access the generated image. This URL points to the final output image created by the API.",
    )
