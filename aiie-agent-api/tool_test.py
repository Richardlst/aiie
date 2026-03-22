import asyncio
import pprint
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
import requests

from app.core.settings import settings

SD_API_URL = settings.SD_API_URL


class SDModel(str, Enum):
    """Image generation models with specific stylistic characteristics."""

    STABLE_DIFFUSION_V1_5 = "runwayml/stable-diffusion-v1-5"  # Versatile base model for general purpose image generation
    DREAMLIKE_PHOTOREAL_2_0 = "dreamlike-art/dreamlike-photoreal-2.0"  # Photorealistic images with enhanced detail
    STABLE_DIFFUSION_XL = "stabilityai/stable-diffusion-xl-base-1.0"  # Higher quality with better composition and details
    SDXL_TURBO = "stabilityai/sdxl-turbo"  # Fast generation with good quality, ideal for quick drafts
    MO_DI_DIFFUSION = (
        "nitrosocke/mo-di-diffusion"  # Modern Disney-inspired animation style
    )
    GHIBLY_DIFFUSION = "nitrosocke/Ghibli-Diffusion"  # Studio Ghibli anime style with soft colors and dreamlike quality
    DISNEY_PIXAL_CARTOON = (
        "stablediffusionapi/disney-pixal-cartoon"  # Pixar/Disney 3D cartoon style
    )


class BaseGenerationRequest(BaseModel):
    prompt: str = Field(
        description="Detailed description of the image you want to generate. Be specific about subject, style, lighting, composition, and mood."
    )
    model: Optional[str] = Field(
        default=SDModel.STABLE_DIFFUSION_V1_5.value,
        description="Model to use for generation. Options include: general purpose (runwayml/stable-diffusion-v1-5), photorealistic (dreamlike-art/dreamlike-photoreal-2.0), high quality (stabilityai/stable-diffusion-xl-base-1.0), fast (stabilityai/sdxl-turbo), Disney style (nitrosocke/mo-di-diffusion), Ghibli anime (nitrosocke/Ghibli-Diffusion), or Pixar-like (stablediffusionapi/disney-pixal-cartoon).",
    )
    negative_prompt: Optional[str] = Field(
        default="",
        description="Elements to avoid in the generated image. Specify unwanted artifacts, styles, or content like 'blurry, distorted faces, bad anatomy, poor quality'.",
    )
    num_inference_steps: Optional[int] = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of denoising steps: 10-20 for speed, 30-50 for quality. Higher values create more detail but take longer.",
    )
    guidance_scale: Optional[float] = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="How strictly to follow the prompt: 1-5 for creative variation, 7-10 for accuracy, 10+ for literal interpretation. Default 7.5 balances creativity and accuracy.",
    )


class Text2ImgRequest(BaseGenerationRequest):
    width: Optional[int] = Field(
        default=512,
        ge=128,
        le=1024,
        description="Width in pixels. Standard options: 512x512 (1:1), 768x512 (3:2), 512x768 (2:3), 1024x1024 (1:1 high-res). Choose based on desired aspect ratio.",
    )
    height: Optional[int] = Field(
        default=512,
        ge=128,
        le=1024,
        description="Height in pixels. Standard options: 512x512 (1:1), 768x512 (3:2), 512x768 (2:3), 1024x1024 (1:1 high-res). Choose based on desired aspect ratio.",
    )


class GenerationResponse(BaseModel):
    image_url: str = Field(description="URL to access the generated image")


@tool(args_schema=Text2ImgRequest)
async def t2i(**kwargs) -> GenerationResponse:
    """
    Generate an image from a text prompt using AI models.

    Choose from different models for specific styles:
    - STABLE_DIFFUSION_V1_5: General purpose, good for most images
    - DREAMLIKE_PHOTOREAL_2_0: Highly detailed photorealistic images
    - STABLE_DIFFUSION_XL: Higher quality with better composition
    - SDXL_TURBO: Fast generation with good quality
    - MO_DI_DIFFUSION: Modern Disney animation style
    - GHIBLY_DIFFUSION: Studio Ghibli anime style
    - DISNEY_PIXAL_CARTOON: Pixar/Disney 3D cartoon style

    Customize with parameters like negative_prompt, guidance_scale and steps.

    Returns:
        URL to the generated image.
    """
    # Convert kwargs into a Text2ImgRequest object
    request = Text2ImgRequest(**kwargs)

    # Get the model value for the API
    model_value = (
        request.model.value
        if isinstance(request.model, SDModel)
        else SDModel.STABLE_DIFFUSION_V1_5.value
    )

    response = requests.post(
        f"{SD_API_URL}/txt2img",
        json={
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
            "width": request.width,
            "height": request.height,
            "model": model_value,
        },
    )

    response_data = response.json()
    response_data = GenerationResponse(**response_data)
    return response_data


tools = [t2i]
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


llm = ChatOllama(
    model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL
).bind_tools(tools)

# Optimized prompt to guide the LLM to produce better results
user_input = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in AI image generation. Your job is to translate user requests into optimal parameters for the t2i image generation tool.

For each request:
1. Analyze what the user wants to create
2. Choose the most appropriate model from the available options in the tool
3. Create a detailed, specific prompt that will generate high-quality results
4. Set appropriate technical parameters (steps, guidance, dimensions)
5. Add a useful negative prompt to avoid common issues

Always select a model from the available SDModel enum options only. Use the model that best matches the desired style and content.""",
        ),
        ("user", "{input}"),
    ]
)

chain = user_input | llm


async def main():
    response = await chain.ainvoke({"input": "Generate an image of a cat"})

    pprint.pprint(response.tool_calls[0]["args"])

    response = await tool_run(response)

    pprint.pprint(response)


if __name__ == "__main__":
    asyncio.run(main())
