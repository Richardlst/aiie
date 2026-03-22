from langchain_core.tools import tool
import aiohttp
from app.api.image.schemas.sr import SrRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse


@tool(args_schema=SrRequest)
async def super_resulution(**kwargs) -> str:
    """
    Upscale an image using AI models to enhance its resolution and quality.

    Returns:
        URL of the segmented image with masks.
    """
    # Convert kwargs into a SegmentRequest object
    request = SrRequest(**kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SRGAN_API_URL}/sr",
            json={
                "image_url": request.image_url,
            },
        ) as response:
            response_data = await response.json()

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
