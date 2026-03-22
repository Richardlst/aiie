from typing import Optional
from pydantic import BaseModel, Field


class InpaintRequest(BaseModel):
    prompt: str = Field(
        title="Prompt",
        description="Detailed description of what content should be generated in the masked areas.",
    )
    image_url: str = Field(
        title="Image Url",
        description="URL of the source image that requires inpainting.",
    )
    mask_url: str = Field(
        title="Mask Url",
        description="URL of the mask image. White = inpaint, Black = keep.",
    )
    reference_image_url: Optional[str] = Field(
        default=None,
        title="Reference Image Url",
        description="Optional reference image for IP-Adapter. If omitted, the source image is used as self-reference to maintain identity/colours.",
    )
    negative_prompt: Optional[str] = Field(
        default="",
        title="Negative Prompt",
        description="Elements to avoid in the inpainted areas.",
    )
    num_inference_steps: Optional[int] = Field(
        default=30,
        ge=1,
        le=100,
        title="Num Inference Steps",
    )
    guidance_scale: Optional[float] = Field(
        default=7.5,
        ge=1,
        le=20,
        title="Guidance Scale",
    )
    strength: Optional[float] = Field(
        default=0.99,
        ge=0,
        le=1,
        title="Strength",
    )
    mask_blur_radius: Optional[int] = Field(
        default=8,
        ge=0,
        le=32,
        title="Mask Blur Radius",
        description="Gaussian blur on mask edges. 0 = hard edges.",
    )
    ip_adapter_scale: Optional[float] = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        title="IP-Adapter Scale",
        description="IP-Adapter influence weight. 1.0 = fully guided by reference image.",
    )
