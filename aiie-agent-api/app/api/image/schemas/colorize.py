from typing import Optional
from pydantic import BaseModel, Field


class ColorizeRequest(BaseModel):
    image_url: str = Field(
        title="Image URL",
        description="URL of the grayscale or black-and-white image to colorize.",
    )
    prompt: Optional[str] = Field(
        default="",
        title="Prompt",
        description="Optional text to guide the colorization style, e.g. 'warm sunset lighting, vibrant colors'. If empty, a caption is generated automatically.",
    )
    negative_prompt: Optional[str] = Field(
        default="low quality, bad quality, low contrast, black and white, bw, monochrome, "
                "grainy, blurry, historical, restored, desaturate",
        title="Negative Prompt",
        description="Terms to avoid in the output.",
    )
    color_intensity: Optional[float] = Field(
        default=1.0,
        ge=0.1,
        le=1.0,
        title="Color Intensity",
        description="Controls how vibrant the colors will be. 1.0 = full color, 0.1 = very subtle.",
    )
    num_inference_steps: Optional[int] = Field(
        default=8,
        ge=1,
        le=50,
        title="Inference Steps",
        description="Number of denoising steps. More steps = slower but potentially better quality.",
    )
    guidance_scale: Optional[float] = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        title="Guidance Scale",
        description="How closely to follow the prompt.",
    )
    seed: Optional[int] = Field(
        default=123,
        title="Seed",
        description="Random seed for reproducible results.",
    )
    append_caption: Optional[bool] = Field(
        default=True,
        title="Append Caption",
        description="Whether to append an auto-generated BLIP caption to the user prompt for richer guidance.",
    )
