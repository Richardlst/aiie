from langchain_core.tools import tool
from app.api.image.schemas.img2img import Img2ImgRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse
from app.utils.http_client import post_json

@tool(args_schema=Img2ImgRequest)
async def img2img(**kwargs) -> str:
    """
    Use this tool ONLY when you need to transform or modify an EXISTING image provided via an image URL. 
    It requires both an 'image_url' and a 'prompt'.
    Do NOT use this tool if the user wants to generate an image from scratch without providing a base image URL.
    
    Returns: URL of the generated image.
    """
    # Convert kwargs into an Img2ImgRequest object
    request = Img2ImgRequest(**kwargs)

    response_data = await post_json(
        f"{settings.SD_API_URL}/img2img",
        {
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
        max_retries=5,
    )

    response_data = GenerationResponse(**response_data)
    return response_data.image_url


