from typing import Optional
from pydantic import BaseModel, Field

from .common import ExpandModel


class ExpandRequest(BaseModel):
    prompt: str = Field(
        title="Prompt",
        description="Detailed description of how the expanded areas should look. Be specific about the content, style, and how it should seamlessly connect to the original image.",
    )
    image_url: str = Field(
        title="Image Url",
        description="URL of the source image you want to expand. This is the base image that will be extended in one or more directions.",
    )
    expand_top: int = Field(
        title="Expand Top",
        description="Number of pixels to expand the image upward. Specifies how much additional content to generate above the original image.",
    )
    expand_bottom: int = Field(
        title="Expand Bottom",
        description="Number of pixels to expand the image downward. Specifies how much additional content to generate below the original image.",
    )
    expand_left: int = Field(
        title="Expand Left",
        description="Number of pixels to expand the image to the left. Specifies how much additional content to generate to the left of the original image.",
    )
    expand_right: int = Field(
        title="Expand Right",
        description="Number of pixels to expand the image to the right. Specifies how much additional content to generate to the right of the original image.",
    )
    model: Optional[ExpandModel] = Field(
        default="runwayml/stable-diffusion-inpainting",
        description="Model to use for expansion. The default model is specialized for seamless content generation at the edges of existing images.",
        title="ExpandModel",
    )
    negative_prompt: Optional[str] = Field(
        default="",
        title="Negative Prompt",
        description="Elements to avoid in the expanded areas. Specify unwanted artifacts, styles, or content like 'blurry, distorted, unrealistic, poor quality'.",
    )
    num_inference_steps: Optional[int] = Field(
        default=50,
        ge=1,
        le=100,
        title="Num Inference Steps",
        description="Number of denoising steps for image expansion. More steps (40-80) produce higher quality expanded areas but take longer. Default is 50 for good quality results.",
    )
    guidance_scale: Optional[float] = Field(
        default=6.0,
        ge=1,
        le=20,
        title="Guidance Scale",
        description="Controls how closely the expanded areas match the style and content of the original image. Higher values create more coherent expansions, while lower values allow more creative variations. Default is 6 for balanced expansion.",
    )
