from langchain_core.tools import tool
from app.api.image.schemas.sr import SrRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse
from app.utils.http_client import post_json


@tool(args_schema=SrRequest)
async def super_resulution(**kwargs) -> str:
    """
    Upscale and sharpen the entire image.
    NOTE: DO NOT use this tool for sharpening human faces (please use gfpgan instead).
    Upscale and sharpen the entire image.
    NOTE: DO NOT use this tool for sharpening human faces (please use gfpgan instead).
    """
    # Convert kwargs into a SrRequest object   
    request = SrRequest(**kwargs)

    response_data = await post_json(
        f"{settings.SRGAN_API_URL}/sr",
        {"image_url": request.image_url},
        max_retries=5,
    )
    
    response_data = GenerationResponse(**response_data)
    return response_data.image_url
