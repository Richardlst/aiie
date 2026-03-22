from typing import Optional
from pydantic import BaseModel, Field

from .common import SDModel


class Img2ImgRequest(BaseModel):
    prompt: str = Field(
        title="Prompt",
        description="Detailed description of how you want the source image to be transformed. Specify desired changes in style, content, or other visual elements.",
    )
    image_url: str = Field(
        title="Image Url",
        description="URL of the source image you want to transform. This is the base image that will be modified according to your prompt.",
    )
    model: Optional[SDModel] = Field(
        default="runwayml/stable-diffusion-v1-5",
        description="Model to use for image transformation. Different models produce different artistic styles and quality levels. Default is Stable Diffusion v1.5 for general-purpose transformations.",
        title="SDModel",
    )
    negative_prompt: Optional[str] = Field(
        default="",
        title="Negative Prompt",
        description="Elements to avoid in the transformed image. Specify unwanted artifacts, styles, or content like 'blurry, distorted faces, bad anatomy, poor quality'.",
    )
    num_inference_steps: Optional[int] = Field(
        default=50,
        ge=1,
        le=100,
        title="Num Inference Steps",
        description="Number of denoising steps for image transformation. More steps (40-80) produce higher quality but take longer. Default is 50 for good quality.",
    )
    guidance_scale: Optional[float] = Field(
        default=9.5,
        ge=1,
        le=20,
        title="Guidance Scale",
        description="How closely the result follows your prompt. Higher values (9-15) produce more literal interpretations, while lower values allow more creative variation. Default is 9.5 for good prompt adherence.",
    )
    strength: Optional[float] = Field(
        default=0.85,
        ge=0,
        le=1,
        title="Strength",
        description="Controls how much to transform the original image: 0.0 makes no changes, 1.0 completely replaces it. Values around 0.7-0.9 typically produce good transformations while preserving the original composition.",
    )
    canny_low_threshold: Optional[int] = Field(
        default=120,
        ge=0,
        le=255,
        title="Canny Low Threshold",
        description="Lower threshold for the Canny edge detection algorithm. Affects which edges are detected in the source image for edge-guided transformation. Lower values detect more edges.",
    )
    canny_high_threshold: Optional[int] = Field(
        default=150,
        ge=0,
        le=255,
        title="Canny High Threshold",
        description="Upper threshold for the Canny edge detection algorithm. Edges above this value are definitely considered for guidance. The threshold pair controls edge sensitivity.",
    )
    controlnet_conditioning_scale: Optional[float] = Field(
        default=0.55,
        ge=0,
        le=1,
        title="Controlnet Conditioning Scale",
        description="Determines how strongly the ControlNet (edge guidance) influences the generation. Higher values preserve more of the original structure and composition. Default 0.55 balances transformation with structure preservation.",
    )
