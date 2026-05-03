from fastapi import APIRouter, HTTPException
import aiohttp
from typing import Dict, Any
import asyncio
import time
import logging

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
logger = logging.getLogger(__name__)

# Global session for connection pooling
_session = None

async def get_session() -> aiohttp.ClientSession:
    """Get or create a persistent aiohttp session with proper configuration."""
    global _session
    if _session is None or _session.closed:
        # Configure timeouts separately (connect, read, write, pool)
        timeout = aiohttp.ClientTimeout(
            total=None,  # No total timeout, use individual timeouts
            connect=30,   # 30 seconds to connect
            sock_connect=30,  # 30 seconds socket connect
            sock_read=60,  # 60 seconds to read data
        )
        
        # Configure connector with TCP keepalive
        connector = aiohttp.TCPConnector(
            limit=100,  # Max connections
            limit_per_host=10,  # Max connections per host
            ttl_dns_cache=300,  # 5 minutes DNS cache
            ssl=False,  # Disable SSL verification for local APIs
            enable_cleanup_closed=True,
            keepalive_timeout=30,  # TCP keepalive timeout
        )
        
        _session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "Connection": "keep-alive",
            }
        )
    return _session


async def close_session():
    """Close the global session."""
    global _session
    if _session and not _session.closed:
        await _session.close()


async def _make_api_request_with_retry(
    endpoint: str,
    data: Dict[Any, Any],
    url: str = settings.SD_API_URL,
    max_retries: int = 5,
    backoff_factor: float = 3.0,
) -> Dict[str, Any]:
    """Make an asynchronous request to the external API with retry logic."""
    
    for attempt in range(max_retries):
        try:
            session = await get_session()
            
            # Đảm bảo không bị dính 2 dấu gạch chéo //
            base_url = url.rstrip('/')
            full_url = f"{base_url}{endpoint}"
            
            # 🟢 MÁY PHÁT HIỆN NÓI DỐI: In ra màn hình địa chỉ thực sự đang bị gọi
            print("\n" + "="*60)
            print(f"🚀 [DEBUG] LẦN {attempt + 1}: Đang bắn API tới -> {full_url}")
            print("="*60 + "\n")
            
            async with session.post(full_url, json=data, ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    # 🟢 Bắt luôn phản hồi của cái server "rởm" đó xem nó nói gì
                    print(f"❌ [DEBUG] LỖI {response.status} TỪ SERVER ĐÓ: {error_text[:200]}")
                    
                    if response.status >= 500 and attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"API returned {response.status}, retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"External API error: {error_text[:500]}",
                        )
        
        except (aiohttp.ClientOSError, aiohttp.ClientConnectionError) as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
                continue
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"Could not connect to image processing service on {url}",
                )
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
                continue
            raise HTTPException(
                status_code=500,
                detail=f"Error processing image: {str(e)}",
            )
    
    raise HTTPException(
        status_code=503,
        detail="Image processing service unavailable",
    )


# Keep old function name for compatibility, but use retry version
async def _make_api_request(
    endpoint: str, data: Dict[Any, Any], url: str = settings.SD_API_URL
) -> Dict[str, Any]:
    """Make an asynchronous request to the external API."""
    return await _make_api_request_with_retry(endpoint, data, url)


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
    result = await _make_api_request("/gfpgan", request.model_dump(exclude_none=True))
    if token_data:
        await result_service.create_(
            Result(
                url=result["image_url"],
                type=ResultType.FR,
                user_id=token_data.sub,
            )
        )
    return GenerationResponse(image_url=result["image_url"])
