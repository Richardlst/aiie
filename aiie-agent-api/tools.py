from typing import Annotated
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage
import requests

from app.core.settings import settings

SRGAN_API_URL = settings.SRGAN_API_URL
SD_API_URL = settings.SD_API_URL


@tool
async def super_resolution(
    image_url: Annotated[str, "The URL of the image to super-resolve."],
) -> str:
    """
    Super-resolve an image.

    Returns:
      str: The URL of the super-resolved image.
    """
    response = requests.post(
        f"{SRGAN_API_URL}/upscale",
        json={"image_url": image_url},
    )

    return response.json()["url"]


@tool
async def txt_2_img(
    prompt: Annotated[str, "The prompt to generate the image"],
    negative_prompt: Annotated[
        str, "The negative prompt to avoid in generation"
    ] = "ugly",
    num_inference_steps: Annotated[
        int, "Number of denoising steps, default is 20"
    ] = 20,
    guidance_scale: Annotated[
        float, "Scale for classifier-free guidance, default is 7.5"
    ] = 7.5,
    width: Annotated[int, "Width of generated image, default is 512"] = 512,
    height: Annotated[int, "Height of generated image, default is 512"] = 512,
) -> str:
    """
    Generate an image from text prompt.

    Returns:
        str: The URL of the generated image.
    """
    response = requests.post(
        f"{SD_API_URL}/txt2img",
        json={
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "width": width,
            "height": height,
        },
    )

    return response.json()["image_url"]


@tool
async def img_2_img(
    prompt: Annotated[str, "The prompt to guide image generation"],
    image_url: Annotated[str, "The URL of the source image"],
    negative_prompt: Annotated[
        str, "The negative prompt to avoid in generation"
    ] = "ugly",
    num_inference_steps: Annotated[
        int, "Number of denoising steps, default is 20"
    ] = 20,
    guidance_scale: Annotated[
        float, "Scale for classifier-free guidance, default is 7.5"
    ] = 7.5,
    strength: Annotated[float, "Strength of the transformation, default is 0.8"] = 0.8,
) -> str:
    """
    Transform an input image based on a text prompt.

    Returns:
        str: The URL of the transformed image.
    """
    response = requests.post(
        f"{SD_API_URL}/img2img",
        json={
            "prompt": prompt,
            "image_url": image_url,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "strength": strength,
        },
    )

    return response.json()["image_url"]


@tool
async def inpaint(
    image_url: Annotated[str, "The URL of the source image"],
    mask_url: Annotated[str, "The URL of the mask image"],
    prompt: Annotated[str, "The prompt to guide image generation"],
    negative_prompt: Annotated[
        str, "The negative prompt to avoid in generation"
    ] = "ugly",
    num_inference_steps: Annotated[int, "Number of denoising steps"] = 2,
    guidance_scale: Annotated[float, "Scale for classifier-free guidance"] = 7.5,
    strength: Annotated[float, "Strength of the transformation"] = 0.8,
) -> str:
    """
    Inpaint an image based on a mask and text prompt.

    Returns:
        str: The URL of the inpainted image.
    """
    response = requests.post(
        f"{SD_API_URL}/inpaint",
        json={
            "prompt": prompt,
            "image_url": image_url,
            "mask_url": mask_url,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "strength": strength,
        },
    )

    return response.json()["image_url"]


@tool
async def segment(
    image_url: Annotated[str, "The URL of the source image"],
    prompts: Annotated[str, "The text prompts to guide segmentation"],
) -> str:
    """
    Segment an image based on text prompts.

    Returns:
        str: The URL of the segmentation mask image.
    """
    response = requests.post(
        f"{SD_API_URL}/segment", json={"image_url": image_url, "prompts": prompts}
    )

    return response.json()["url"]


tools = [super_resolution, txt_2_img, img_2_img, inpaint, segment]

tools_dict = {tool.name: tool for tool in tools}


async def tool_run(message: AIMessage) -> list[ToolMessage]:
    tool_calls = message.tool_calls
    tool_messages = []
    for tool_call in tool_calls:
        tool = tools_dict[tool_call["name"]]
        result = await tool.ainvoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    return tool_messages