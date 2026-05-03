from langchain_core.tools import tool
from app.api.image.schemas.segment import SegmentRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse
from app.utils.http_client import post_json


@tool(args_schema=SegmentRequest)
async def segment(**kwargs) -> str:
    """
    Segment specific objects or regions in an image using AI.

    Returns:
        URL of the segmented image with masks.
    """
    # Convert kwargs into a SegmentRequest object
    request = SegmentRequest(**kwargs)

    response_data = await post_json(
        f"{settings.SD_API_URL}/segment",
        {
            "image_url": request.image_url,
            "prompts": request.prompts,
        },
        max_retries=5,
    )

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
