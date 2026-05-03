from langchain_core.tools import tool
from app.api.image.schemas.sr import SrRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse
from app.utils.http_client import post_json

@tool(args_schema=SrRequest)
async def gfpgan(**kwargs) -> str:
    """
        SPECIALIZED tool for restoring and sharpening HUMAN FACES.
        Call this tool when the user requests 'sharpen face', 'restore portrait', or 'fix face'.
    """
    request = SrRequest(**kwargs)
    response_data = await post_json(
        f"{settings.SD_API_URL}/gfpgan",
        {"image_url": request.image_url},
        max_retries=5,
    )

    response_data = GenerationResponse(**response_data)
    return response_data.image_url