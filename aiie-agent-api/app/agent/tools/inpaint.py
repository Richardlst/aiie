from langchain_core.tools import tool
from app.api.image.schemas.inpaint import InpaintRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse
from app.utils.http_client import post_json


@tool(args_schema=InpaintRequest)
async def inpaint(**kwargs) -> str:
    """
    Fill in or replace specific areas of an image using AI based on text description.

    Customize with parameters like strength, guidance_scale and edge control thresholds.

    Returns:
        URL of the generated image.
    """
    # Convert kwargs into an InpaintRequest object
    request = InpaintRequest(**kwargs)

    response_data = await post_json(
        f"{settings.SD_API_URL}/inpaint",
        {
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "image_url": request.image_url,
            "mask_url": request.mask_url,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
            "strength": request.strength,
        },
        max_retries=5,
    )

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
