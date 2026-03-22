from typing import Optional
from pydantic import BaseModel, Field

from .common import SDModel


class Text2ImgRequest(BaseModel):
    prompt: str = Field(
        title="Prompt",
        description="Detailed description of the image you want to generate. Be specific about subject, style, lighting, composition, and mood for best results.",
    )
    model: Optional[SDModel] = Field(
        default="runwayml/stable-diffusion-v1-5",
        description="Model to use for image generation. Different models produce different artistic styles and quality levels. Default is Stable Diffusion v1.5 which provides good quality general-purpose images.",
        title="SDModel",
    )
    negative_prompt: Optional[str] = Field(
        default="",
        title="Negative Prompt",
        description="Elements to avoid in the generated image. Specify unwanted artifacts, styles, or content like 'blurry, distorted faces, bad anatomy, poor quality'.",
    )
    num_inference_steps: Optional[int] = Field(
        default=20,
        ge=1,
        le=100,
        title="Num Inference Steps",
        description="Number of denoising steps: 10-20 for speed, 30-50 for quality. Higher values create more detail but take longer to generate.",
    )
    guidance_scale: Optional[float] = Field(
        default=7.5,
        ge=1,
        le=20,
        title="Guidance Scale",
        description="How strictly to follow the prompt: 1-5 for creative variation, 7-10 for accuracy, 10+ for literal interpretation. Default 7.5 balances creativity and accuracy.",
    )
    width: Optional[int] = Field(
        default=512,
        ge=128,
        le=1024,
        title="Width",
        description="Width in pixels. Standard options: 512x512 (1:1), 768x512 (3:2), 512x768 (2:3), 1024x1024 (1:1 high-res). Choose based on desired aspect ratio.",
    )
    height: Optional[int] = Field(
        default=512,
        ge=128,
        le=1024,
        title="Height",
        description="Height in pixels. Standard options: 512x512 (1:1), 768x512 (3:2), 512x768 (2:3), 1024x1024 (1:1 high-res). Choose based on desired aspect ratio.",
    )
