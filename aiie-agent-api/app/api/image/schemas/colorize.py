from typing import Optional
from pydantic import BaseModel, Field

class ColorizeRequest(BaseModel):
    image_url: str = Field(
        title="Image URL",
        description="URL of the grayscale or black-and-white image to colorize.",
    )
    prompt: Optional[str] = Field(
        default="RAW photo, (colorized:1.3), highly detailed, realistic vibrant colors, natural skin tone, 8k uhd, dslr, soft lighting, high quality",
        title="Prompt",
        description="Text to guide the colorization style. Defaults are optimized for Realistic Vision.",
    )
    negative_prompt: Optional[str] = Field(
        default="(grayscale:1.5), (black and white:1.5), monochrome, sepia, vintage, old photo, faded, distorted, artifacts",
        title="Negative Prompt",
        description="Terms to avoid in the output. Strictly forces the model to generate colors.",
    )
    denoising_strength: Optional[float] = Field(
        default=0.75,
        ge=0.1,
        le=1.0,
        title="Denoising Strength",
        description="Crucial for Img2Img. 0.75-0.85 is optimal when using ControlNet Recolor. If NOT using ControlNet, drop to 0.45-0.55.",
    )
    controlnet_weight: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        title="ControlNet Weight",
        description="Weight for the ControlNet Recolor model to preserve image structure.",
    )
    num_inference_steps: Optional[int] = Field(
        default=20, 
        ge=1,
        le=50,
        title="Inference Steps",
        description="Number of denoising steps. 20-25 is the sweet spot for DPM++ 2M Karras on SD 1.5.",
    )
    guidance_scale: Optional[float] = Field(
        default=7.0,
        ge=1.0,
        le=20.0,
        title="Guidance Scale",
        description="How closely to follow the prompt. 7.0 is standard for Realistic Vision.",
    )
    max_dimension: Optional[int] = Field(
        default=768,
        ge=512,
        le=768,
        title="Max Dimension",
        description="Caps the longest edge of the image to prevent Out of Memory errors on 4GB VRAM.",
    )
    seed: Optional[int] = Field(
        default=-1,
        title="Seed",
        description="Random seed for reproducible results. Use -1 for a random seed.",
    )
    append_caption: Optional[bool] = Field(
        default=True,
        title="Append Caption",
        description="Whether to append an auto-generated BLIP caption to the user prompt for richer guidance.",
    )