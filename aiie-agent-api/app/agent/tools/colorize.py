from langchain_core.tools import tool
# Giả định bạn đã tạo schema ColorizeRequest tương tự các schema trước
from app.api.image.schemas.colorize import ColorizeRequest 
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse
from app.utils.http_client import post_json

@tool(args_schema=ColorizeRequest)
async def colorize(**kwargs) -> str:
    """
    Use this tool ONLY to add color to black and white (grayscale) images or to restore color to old photographs.
    
    This tool requires an 'image_url' of a grayscale image. You can optionally provide a 'prompt' 
    to guide the AI on specific colors (e.g., 'blue suit, green trees').
    
    Do NOT use this tool for general image transformation or generating new images from scratch.
    
    Returns:
        URL of the colorized (color-restored) image.
    """
    
    request = ColorizeRequest(**kwargs)
    response_data = await post_json(
        f"{settings.SD_API_URL}/colorize", 
        {
            "image_url": request.image_url,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
        },
        max_retries=5,
    )
    response_data = GenerationResponse(**response_data)
    return response_data.image_url