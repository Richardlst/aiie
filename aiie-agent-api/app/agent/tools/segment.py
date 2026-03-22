from langchain_core.tools import tool
import aiohttp
from app.api.image.schemas.segment import SegmentRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse


@tool(args_schema=SegmentRequest)
async def segment(**kwargs) -> str:
    """
    Segment specific objects or regions in an image using AI.

    Returns:
        URL of the segmented image with masks.
    """
    # Convert kwargs into a SegmentRequest object
    request = SegmentRequest(**kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SD_API_URL}/segment",
            json={
                "image_url": request.image_url,
                "prompts": request.prompts,
            },
        ) as response:
            response_data = await response.json()

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
