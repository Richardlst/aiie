from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import socket
import sys
import os
import torch

# Windows socket buffer fix - increase buffer sizes
if sys.platform == "win32":
    try:
        # Increase TCP socket buffer sizes for Windows
        socket.socket.SO_SNDBUF = 8 * 1024 * 1024  # 8MB
        socket.socket.SO_RCVBUF = 8 * 1024 * 1024  # 8MB
        os.environ["HF_DATASETS_TRUST_REMOTE_CODE"] = "1"
        # Increase Windows page file (virtual memory) to prevent paging errors
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
    except Exception as e:
        pass

# Configure PyTorch threading ONCE at startup (before models load)
# This must be done before any parallel work starts
_num_threads = max(1, (os.cpu_count() or 4) // 2)
torch.set_num_threads(_num_threads)
try:
    torch.set_num_interop_threads(max(1, _num_threads // 2))
except RuntimeError:
    pass  # Already set or parallel work started

from app.dependencies import (
    ExpandServiceDep,
    Img2ImgServiceDep,
    InpaintServiceDep,
    Txt2ImgServiceDep,
    ColorizeServiceDep,
    FaceRefineServiceDep,
)
from app.dependencies.segment import SegmentationServiceDep
from app.logger import setup_logger

from .models import (
    ExpandRequest,
    FaceRefineRequest,
    SegmentRequest,
    Text2ImgRequest,
    Img2ImgRequest,
    InpaintRequest,
    ColorizeRequest,
    GenerationResponse,
)


# Thiết lập logging
logger = setup_logger("Main")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/txt2img", response_model=GenerationResponse)
async def generate_image(request: Text2ImgRequest, service: Txt2ImgServiceDep):
    url = await service.run(request)
    return GenerationResponse(image_url=url)


@app.post("/img2img", response_model=GenerationResponse)
async def image_to_image(request: Img2ImgRequest, service: Img2ImgServiceDep):
    url = await service.run(request)
    return GenerationResponse(image_url=url)


@app.post("/inpaint", response_model=GenerationResponse)
async def inpaint_image(request: InpaintRequest, service: InpaintServiceDep):
    try:
        logger.info(f"Inpaint request: image={request.image_url}, mask={request.mask_url}")
        url = await service.run(request)
        logger.info(f"Inpaint success: {url}")
        return GenerationResponse(image_url=url)
    except Exception as e:
        logger.error(f"Inpaint error: {str(e)}", exc_info=True)
        raise


@app.post("/expand", response_model=GenerationResponse)
async def expand_image(request: ExpandRequest, service: ExpandServiceDep):
    try:
        logger.info(f"Expand request: image={request.image_url}, L={request.expand_left} R={request.expand_right} T={request.expand_top} B={request.expand_bottom}")
        url = await service.run(request)
        logger.info(f"Expand success: {url}")
        return GenerationResponse(image_url=url)
    except Exception as e:
        logger.error(f"Expand error: {str(e)}", exc_info=True)
        raise


@app.post("/segment", response_model=GenerationResponse)
async def segment_image(request: SegmentRequest, service: SegmentationServiceDep):
    url = await service.run(request)
    return GenerationResponse(image_url=url)


@app.post("/colorize", response_model=GenerationResponse)
async def colorize_image(request: ColorizeRequest, service: ColorizeServiceDep):
    try:
        logger.info(f"Colorize request: image={request.image_url}, prompt={request.prompt}")
        url = await service.run(request)
        logger.info(f"Colorize success: {url}")
        return GenerationResponse(image_url=url)
    except asyncio.CancelledError:
        logger.error(f"Colorize cancelled (socket timeout/network issue) - retrying may help")
        raise
    except asyncio.CancelledError:
        logger.error(f"Colorize cancelled (socket timeout/network issue) - retrying may help")
        raise
    except Exception as e:
        logger.error(f"Colorize error: {str(e)}", exc_info=True)
        raise


@app.post("/gfpgan", response_model=GenerationResponse)
async def face_refine_image(request: FaceRefineRequest, service: FaceRefineServiceDep):
    try:
        logger.info(
            f"Face-refine request: image={request.image_url}, "
            f"upscale={request.upscale}, weight={request.weight}"
        )
        url = await service.run(request)
        logger.info(f"Face-refine success: {url}")
        return GenerationResponse(image_url=url)
    except Exception as e:
        logger.error(f"Face-refine error: {str(e)}", exc_info=True)
        raise
