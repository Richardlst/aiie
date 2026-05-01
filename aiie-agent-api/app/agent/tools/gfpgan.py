from langchain_core.tools import tool
import aiohttp
from app.api.image.schemas.sr import SrRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse

@tool(args_schema=SrRequest)
async def gfpgan(**kwargs) -> str:
    """
        SPECIALIZED tool for restoring and sharpening HUMAN FACES.
        Call this tool when the user requests 'sharpen face', 'restore portrait', or 'fix face'.
    """
    request = SrRequest(**kwargs)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SD_API_URL}/gfpgan", 
            json={"image_url": request.image_url},
        ) as response:
            response_data = await response.json()

    response_data = GenerationResponse(**response_data)
    return response_data.image_url