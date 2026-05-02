from langchain_core.tools import tool

from app.api.image.schemas.common import GenerationResponse
from app.api.image.schemas.expand import ExpandRequest
from app.core.settings import settings
from app.utils.http_client import post_json


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

    response_data = await post_json(
        f"{settings.SD_API_URL}/expand",
        {
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
        max_retries=5,
    )

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
