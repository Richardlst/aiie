"""Face Refinement Service using GFPGAN.

GFPGAN (Generative Facial Prior GAN) restores degraded / low-quality faces
and can simultaneously super-resolve the full image.

Model: GFPGANv1.4  (downloaded once from GitHub Releases, ~350 MB)
Library: pip install gfpgan

Pipeline is loaded lazily on the first request and cached for the lifetime of
the server process.  Inference runs in a dedicated thread-pool executor so the
FastAPI event loop is never blocked.
"""

import asyncio
import concurrent.futures
import gc
import os
from typing import Any

import cv2
import numpy as np
import PIL.Image

from app.models import FaceRefineRequest
from app.service.base_sd import BaseSDService
from app.logger import setup_logger

logger = setup_logger("FaceRefineService")

# ---------------------------------------------------------------------------
# GFPGAN v1.4 weights – downloaded from GitHub Releases on first use.
# The gfpgan package will cache them in the current working directory under
# experiments/pretrained_models/GFPGANv1.4.pth
# ---------------------------------------------------------------------------
GFPGAN_MODEL_URL = (
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"
)
GFPGAN_MODEL_PATH = os.path.join("models", "GFPGANv1.4.pth")

# Thread-pool: single worker to avoid OOM from concurrent face-enhancement jobs
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(
    max_workers=1, thread_name_prefix="face_refine"
)

# Module-level cache – loaded once on first request
_restorer: Any = None


def _get_or_load_restorer(upscale: int = 2) -> Any:
    """Load GFPGANer and cache it.  Downloads weights if not already present."""
    global _restorer

    if _restorer is not None:
        return _restorer

    # Ensure the model directory exists
    os.makedirs("models", exist_ok=True)

    # Download model weights if missing
    if not os.path.exists(GFPGAN_MODEL_PATH):
        logger.info(f"Downloading GFPGAN weights → {GFPGAN_MODEL_PATH}")
        import urllib.request
        urllib.request.urlretrieve(GFPGAN_MODEL_URL, GFPGAN_MODEL_PATH)
        logger.info("GFPGAN weights downloaded.")

    from gfpgan import GFPGANer

    _restorer = GFPGANer(
        model_path=GFPGAN_MODEL_PATH,
        upscale=upscale,
        arch="clean",
        channel_multiplier=2,
        bg_upsampler=None,  # skip background upsampling to save VRAM / time
    )
    logger.info("GFPGANer ready.")
    return _restorer


def _sync_face_refine(request: FaceRefineRequest, image: PIL.Image.Image) -> PIL.Image.Image:
    """Blocking face restoration – executed in a dedicated thread."""
    gc.collect()

    restorer = _get_or_load_restorer(upscale=request.upscale)

    # Convert PIL (RGB) → OpenCV (BGR) as required by GFPGAN
    img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    logger.info(
        f"Enhancing faces – upscale={request.upscale}, "
        f"only_center_face={request.only_center_face}, weight={request.weight}"
    )

    _, _, restored_img = restorer.enhance(
        img_bgr,
        has_aligned=False,
        only_center_face=request.only_center_face,
        paste_back=True,
        weight=request.weight,
    )

    if restored_img is None:
        logger.warning("GFPGAN returned no output – returning the original image.")
        return image

    # Convert back: BGR → RGB → PIL
    result_pil = PIL.Image.fromarray(cv2.cvtColor(restored_img, cv2.COLOR_BGR2RGB))
    logger.info(f"Face refinement complete – output size: {result_pil.size}")
    return result_pil


class FaceRefineService(BaseSDService):
    """Restore and enhance faces in an image using GFPGAN v1.4.

    Features
    --------
    • Blind face restoration (works on low-quality / compressed inputs)
    • Optional super-resolution (upscale 1–4×)
    • Weight parameter to control restored-vs-original identity balance
    • Model weight is downloaded once from GitHub Releases and cached locally
    """

    async def run(self, request: FaceRefineRequest) -> str:
        image = await self.process_image_url(request.image_url)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _EXECUTOR,
            _sync_face_refine,
            request,
            image,
        )

        self._debug_image(result, "face_refine")
        return await self.save_image(result)
