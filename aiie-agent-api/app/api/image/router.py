from fastapi import APIRouter, HTTPException
import aiohttp
from typing import Dict, Any

from app.api.auth.dependencies import AuthenticateOrNoneDep
from app.api.image.schemas.sr import SrRequest
from app.api.result.dependencies.get_result_base_service import ResultBaseServiceDep
from app.api.result.models.result import Result
from app.api.result.schemas.result_type import ResultType
from app.core.settings import settings

from .schemas import (
    Text2ImgRequest,
    Img2ImgRequest,
    InpaintRequest,
    ExpandRequest,
    SegmentRequest,
    GenerationResponse,
    ColorizeRequest,
    FaceRefineRequest,
)

router = APIRouter(prefix="/image", tags=["image"])


async def _make_api_request(
    endpoint: str, data: Dict[Any, Any], url: str = settings.SD_API_URL
) -> Dict[str, Any]:
    """Make an asynchronous request to the external API."""
    timeout = aiohttp.ClientTimeout(total=1200)  # 20 minutes timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        url = f"{url}{endpoint}"
        async with session.post(url, json=data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"External API error: {error_text}",
                )
            return await response.json()


@router.post("/sr", response_model=GenerationResponse)
async def upscale_image(
    request: SrRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Upscale an image using super-resolution."""
    result = await _make_api_request(
        "/sr", request.model_dump(exclude_none=True), url=settings.SRGAN_API_URL
    )
    if token_data:
        # Save the generated image URL to the database
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.SR,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])


@router.post("/txt2img")
async def generate_image_from_text(
    request: Text2ImgRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Generate an image from text prompt."""
    result = await _make_api_request("/txt2img", request.model_dump(exclude_none=True))
    if token_data:
        # Save the generated image URL to the database
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.T2I,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])


@router.post("/img2img", response_model=GenerationResponse)
async def generate_image_from_image(
    request: Img2ImgRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Transform an existing image based on a text prompt."""
    result = await _make_api_request("/img2img", request.model_dump(exclude_none=True))
    if token_data:
        # Save the generated image URL to the database
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.I2I,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])


@router.post("/inpaint", response_model=GenerationResponse)
async def inpaint_image(
    request: InpaintRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Inpaint parts of an image based on a mask."""
    result = await _make_api_request("/inpaint", request.model_dump(exclude_none=True))
    if token_data:
        # Save the generated image URL to the database
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.INP,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])


@router.post("/expand", response_model=GenerationResponse)
async def expand_image(
    request: ExpandRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Expand an image in specified directions."""
    result = await _make_api_request("/expand", request.model_dump(exclude_none=True))
    if token_data:
        # Save the generated image URL to the database
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.EXP,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])


@router.post("/segment", response_model=GenerationResponse)
async def segment_image(
    request: SegmentRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Segment an image based on given prompts."""
    result = await _make_api_request("/segment", request.model_dump(exclude_none=True))
    if token_data:
        # Save the generated image URL to the database
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.SEG,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])


@router.post("/colorization", response_model=GenerationResponse)
async def colorize_image(
    request: ColorizeRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Colorize a grayscale or black-and-white image guided by a text prompt."""
    result = await _make_api_request("/colorize", request.model_dump(exclude_none=True))
    if token_data:
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.COL,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])


@router.post("/face-refine", response_model=GenerationResponse)
async def face_refine_image(
    request: FaceRefineRequest,
    result_service: ResultBaseServiceDep,
    token_data: AuthenticateOrNoneDep = None,
):
    """Restore and enhance faces in an image using GFPGAN."""
    result = await _make_api_request("/face-refine", request.model_dump(exclude_none=True))
    if token_data:
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.FR,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])
