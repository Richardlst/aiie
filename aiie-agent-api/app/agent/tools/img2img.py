from langchain_core.tools import tool
import aiohttp
from app.api.image.schemas.img2img import Img2ImgRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse

@tool(args_schema=Img2ImgRequest)
async def img2img(**kwargs) -> str:
    """
    Transform an existing image based on text description using AI.
    
    Customize with parameters like strength, guidance_scale and edge control thresholds.
    
    Returns:
        URL of the generated image.
    """
    # Convert kwargs into an Img2ImgRequest object
    request = Img2ImgRequest(**kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.SD_API_URL}/img2img",
            json={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "image_url": request.image_url,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "strength": request.strength,
                "canny_low_threshold": request.canny_low_threshold,
                "canny_high_threshold": request.canny_high_threshold,
                "controlnet_conditioning_scale": request.controlnet_conditioning_scale,
            },
        ) as response:
            response_data = await response.json()

    response_data = GenerationResponse(**response_data)
    return response_data.image_url


