from typing import Optional
from pydantic import BaseModel, Field


class FaceRefineRequest(BaseModel):
    image_url: str = Field(
        title="Image URL",
        description="URL of the image containing faces to restore/enhance.",
    )
    upscale: Optional[int] = Field(
        default=2,
        ge=1,
        le=4,
        title="Upscale",
        description="Super-resolution upscale factor (1–4).",
    )
    only_center_face: Optional[bool] = Field(
        default=False,
        title="Only Center Face",
        description="If True, only the largest/center face is restored.",
    )
    weight: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        title="Weight",
        description="Balance between restored detail (1.0) and original identity (0.0).",
    )
