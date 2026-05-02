from pydantic import BaseModel, Field
from typing import Optional


class BaseGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = Field(default="")
    num_inference_steps: Optional[int] = Field(default=20, ge=1, le=100)
    guidance_scale: Optional[float] = Field(default=7.5, ge=1.0, le=20.0)


class Text2ImgRequest(BaseGenerationRequest):
    width: Optional[int] = Field(default=512, ge=128, le=1024)
    height: Optional[int] = Field(default=512, ge=128, le=1024)


class Img2ImgRequest(BaseGenerationRequest):
    image_url: str
    guidance_scale: Optional[float] = Field(default=9.5, ge=1.0, le=20.0)
    num_inference_steps: Optional[int] = Field(default=50, ge=1, le=100)
    strength: Optional[float] = Field(default=0.85, ge=0.0, le=1.0)
    canny_low_threshold: Optional[int] = Field(default=120, ge=0, le=255)
    canny_high_threshold: Optional[int] = Field(default=150, ge=0, le=255)
    controlnet_conditioning_scale: Optional[float] = Field(default=0.55, ge=0.0, le=1.0)


class InpaintRequest(BaseGenerationRequest):
    image_url: str
    mask_url: str
    reference_image_url: Optional[str] = Field(
        default=None,
        description="Reference image for IP-Adapter. If omitted, the source image is used as self-reference.",
    )
    guidance_scale: Optional[float] = Field(default=7.5, ge=1.0, le=20.0)
    num_inference_steps: Optional[int] = Field(default=30, ge=1, le=100)
    strength: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    mask_blur_radius: Optional[int] = Field(
        default=16, ge=0, le=32,
        description="Gaussian blur radius applied to mask edges for softer transitions (16+ recommended).",
    )
    ip_adapter_scale: Optional[float] = Field(
        default=0.0, ge=0.0, le=1.0,
        description="IP-Adapter influence weight. 1.0 = fully guided by reference image.",
    )


class ExpandRequest(BaseGenerationRequest):
    image_url: str
    expand_top: int
    expand_bottom: int
    expand_left: int
    expand_right: int
    num_inference_steps: Optional[int] = Field(default=50, ge=1, le=100)
    guidance_scale: Optional[float] = Field(default=6, ge=1.0, le=20.0)


class ColorizeRequest(BaseModel):
    image_url: str = Field(description="URL of the grayscale or B&W image to colorize.")
    prompt: Optional[str] = Field(
        default="",
        description="Optional text to guide colorization style. Leave empty for BLIP auto-caption.",
    )
    negative_prompt: Optional[str] = Field(
        default="low quality, bad quality, low contrast, black and white, bw, monochrome, "
                "grainy, blurry, historical, restored, desaturate",
        description="Terms to avoid in the output.",
    )
    num_inference_steps: Optional[int] = Field(
        default=4, ge=1, le=50,
        description="Number of denoising steps. 4 is optimal for SDXL-Lightning 4-step.",
    )
    guidance_scale: Optional[float] = Field(
        default=7.5, ge=1.0, le=20.0,
        description="How closely to follow the prompt.",
    )
    color_intensity: Optional[float] = Field(
        default=1.0, ge=0.1, le=1.0,
        description="Controls vibrancy. 1.0 = full color, 0.1 = very subtle.",
    )
    seed: Optional[int] = Field(
        default=123,
        description="Random seed for reproducible results.",
    )
    append_caption: Optional[bool] = Field(
        default=True,
        description="Whether to append an auto-generated BLIP caption to the user prompt.",
    )


class SegmentRequest(BaseModel):
    image_url: str
    prompts: str


class FaceRefineRequest(BaseModel):
    image_url: str = Field(description="URL of the image containing faces to restore/enhance.")
    upscale: Optional[int] = Field(
        default=2, ge=1, le=4,
        description="Super-resolution upscale factor (1–4).",
    )
    only_center_face: Optional[bool] = Field(
        default=False,
        description="If True, only the largest/center face is restored.",
    )
    weight: Optional[float] = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Balance between restored detail (1.0) and original identity (0.0).",
    )


class GenerationResponse(BaseModel):
    image_url: str


class UploadImage(BaseModel):
    filename: str
    url: str


class UploadResponse(BaseModel):
    data: UploadImage

class UploadMultipleResponse(BaseModel):
    data: list[UploadImage]
