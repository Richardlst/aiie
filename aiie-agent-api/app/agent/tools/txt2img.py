from langchain_core.tools import tool
import aiohttp
from app.api.image.schemas.txt2img import Text2ImgRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse


@tool(args_schema=Text2ImgRequest)
async def text2img(**kwargs) -> str:
    """
    Generate an image from a text prompt using AI models.

    Customize with parameters like negative_prompt, guidance_scale and steps.

    Returns:
        URL to the generated image.
    """
    # Convert kwargs into a Text2ImgRequest object
    request = Text2ImgRequest(**kwargs)

    # return "http://example.com/image.jpg"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SD_API_URL}/txt2img",
            json={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "width": request.width,
                "height": request.height,
            },
        ) as response:
            response_data = await response.json()

    response_data = GenerationResponse(**response_data)
    return response_data.image_url
