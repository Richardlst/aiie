from langchain_core.tools import tool
from app.api.image.schemas.txt2img import Text2ImgRequest
from app.core.settings import settings
from app.api.image.schemas.common import GenerationResponse
from app.utils.http_client import post_json


@tool(args_schema=Text2ImgRequest)
async def text2img(**kwargs) -> str:
    """
    Use this tool ONLY to generate a completely NEW image from scratch based on a text description.
    
    Do NOT use this tool if the user provides an image URL or wants to modify, edit, or transform an EXISTING image (use the 'img2img' tool for that instead).

    Customize with parameters like negative_prompt, guidance_scale and steps.

    Returns:
        URL to the generated image.
    """
    # Convert kwargs into a Text2ImgRequest object
    request = Text2ImgRequest(**kwargs)

    response_data = await post_json(
        f"{settings.SD_API_URL}/txt2img",
        {
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
            "width": request.width,
            "height": request.height,
        },
        max_retries=5,
    )

    response_data = GenerationResponse(**response_data)
    return response_data.image_url