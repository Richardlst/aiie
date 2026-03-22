from langchain_core.tools import tool
import aiohttp

from app.api.image.schemas.common import GenerationResponse
from app.api.image.schemas.expand import ExpandRequest
from app.core.settings import settings


@tool(args_schema=ExpandRequest)
async def expand(**kwargs) -> str:
    """
    Expand an image in one or more directions using AI.

    Customize with parameters like expand dimensions and generation settings.

    Returns:
        URL of the expanded image.
    """
    # Convert kwargs into an ExpandRequest object
    request = ExpandRequest(**kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SD_API_URL}/expand",
            json={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "image_url": request.image_url,
                "expand_top": request.expand_top,
                "expand_bottom": request.expand_bottom,
                "expand_left": request.expand_left,
                "expand_right": request.expand_right,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
            },
        ) as response:
            response_data = await response.json()

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
