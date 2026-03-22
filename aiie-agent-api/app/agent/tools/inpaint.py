from langchain_core.tools import tool
import aiohttp
from app.api.image.schemas.inpaint import InpaintRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse


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

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SD_API_URL}/inpaint",
            json={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "image_url": request.image_url,
                "mask_url": request.mask_url,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "strength": request.strength,
            },
        ) as response:
            response_data = await response.json()

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
