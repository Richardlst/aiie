import gc
from typing import Any, Optional

import numpy as np
import torch
from PIL import Image, ImageFilter
from diffusers import StableDiffusionInpaintPipeline, DDIMScheduler

from app.models import InpaintRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("InpaintService")
device = settings.DEVICE

# Plain SD-inpainting — NO ControlNet.
# ControlNet control_v11p_sd15_inpaint is designed to *preserve* original
# structure, which causes it to reproduce cracks/tears instead of removing them.
BASE_MODEL_ID        = "runwayml/stable-diffusion-inpainting"
IP_ADAPTER_REPO      = "h94/IP-Adapter"
IP_ADAPTER_SUBFOLDER = "models"
IP_ADAPTER_WEIGHT    = "ip-adapter_sd15.bin"

_pipe_cache: Optional[Any] = None


def _load_pipe() -> StableDiffusionInpaintPipeline:
    global _pipe_cache
    if _pipe_cache is not None:
        return _pipe_cache

    if device == "cuda":
        gc.collect()
        torch.cuda.empty_cache()

    torch_dtype = torch.float16 if device == "cuda" else torch.float32
    variant = "fp16" if device == "cuda" else None

    logger.info("Loading SD inpaint pipeline…")
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch_dtype,
        safety_checker=None,
        variant=variant,
    )

    pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
    pipe.vae.enable_slicing()

    # Load IP-Adapter BEFORE enable_model_cpu_offload so image_encoder is
    # registered and can be pinned to CUDA afterward.
    # Must also be before any attention-slicing (conflicts with IPAdapterAttnProcessor).
    logger.info("Loading IP-Adapter…")
    pipe.load_ip_adapter(
        IP_ADAPTER_REPO,
        subfolder=IP_ADAPTER_SUBFOLDER,
        weight_name=IP_ADAPTER_WEIGHT,
        image_encoder_folder="models/image_encoder",
    )
    logger.info("IP-Adapter loaded.")

    if device == "cuda":
        pipe.enable_model_cpu_offload()
        # image_encoder is not included in cpu-offload — keep it on CUDA.
        if pipe.image_encoder is not None:
            pipe.image_encoder.to(device)
        try:
            pipe.enable_xformers_memory_efficient_attention()
            logger.info("xformers enabled.")
        except Exception:
            logger.warning("xformers not available.")
    else:
        pipe.to("cpu")

    _pipe_cache = pipe
    logger.info("Inpaint pipeline (SD-inpainting + IP-Adapter) ready.")
    return pipe


def _dilate_mask(mask: Image.Image, radius: int) -> Image.Image:
    """Morphological dilation: expand white (masked) regions by `radius` pixels.

    Uses MaxFilter with kernel size = 2*radius+1.  This ensures that the torn
    boundary — which may have fractional coverage in the feathered mask — ends
    up fully *inside* the inpainted region during compositing.
    """
    if radius <= 0:
        return mask
    kernel = 2 * radius + 1
    return mask.filter(ImageFilter.MaxFilter(kernel))


def _feather_mask(mask: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return mask
    return mask.filter(ImageFilter.GaussianBlur(radius=radius))


def _composite_with_original(
    original: Image.Image,
    inpainted: Image.Image,
    mask: Image.Image,
) -> Image.Image:
    orig_np = np.array(original.convert("RGB"), dtype=np.float32)
    inp_np  = np.array(inpainted.convert("RGB"), dtype=np.float32)
    msk_np  = np.array(mask.convert("L"), dtype=np.float32)[:, :, None] / 255.0
    blended = inp_np * msk_np + orig_np * (1.0 - msk_np)
    return Image.fromarray(blended.clip(0, 255).astype(np.uint8))


def _make_clean_reference(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Fill masked (damaged) regions with the average colour of the unmasked area.

    Used when no external reference image is provided — this prevents the CLIP
    image encoder from encoding cracks/tears as features to reproduce.
    """
    img_arr  = np.array(image.convert("RGB"), dtype=np.float32)
    msk_arr  = np.array(mask.convert("L"), dtype=np.float32) / 255.0   # 1=inpaint, 0=keep

    # Compute mean colour of the undamaged pixels only
    keep_mask = (1.0 - msk_arr) > 0.5
    if keep_mask.any():
        mean_color = img_arr[keep_mask].mean(axis=0)   # shape (3,)
    else:
        mean_color = np.array([127.0, 127.0, 127.0])

    # Replace masked pixels with that mean colour
    clean = img_arr.copy()
    clean[msk_arr > 0.5] = mean_color
    return Image.fromarray(clean.clip(0, 255).astype(np.uint8))


class InpaintService(BaseSDService):
    async def run(self, input: InpaintRequest) -> str:
        if device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        pipe = _load_pipe()

        image    = await self.process_image_url(input.image_url)
        mask_raw = await self.process_image_url(input.mask_url)

        original_size = image.size
        image    = self._resize_image(image).convert("RGB")
        mask_raw = mask_raw.resize(image.size, Image.LANCZOS).convert("L")
        input    = self._upgrade_prompt(input)

        blur_radius = input.mask_blur_radius if input.mask_blur_radius is not None else 8

        w = image.width  // 8 * 8
        h = image.height // 8 * 8
        image_sd    = image.resize((w, h), Image.LANCZOS)
        mask_raw_sd = mask_raw.resize((w, h), Image.LANCZOS)

        # Pre-fill pipeline input: replace masked pixels (torn paper, cracks)
        # with the mean colour of the undamaged region before passing to SD.
        # This removes torn-paper context at the mask boundary so the pipeline
        # doesn't reproduce the tear shape in its generated output.
        # We dilate slightly before filling to also hide the torn border pixels
        # that sit just outside the raw mask.
        fill_mask     = _dilate_mask(mask_raw_sd, radius=blur_radius)
        image_sd_fill = _make_clean_reference(image_sd, fill_mask)

        # SD pipeline mask: feather over the fill mask so generation blends smoothly
        mask_sd = _feather_mask(fill_mask, radius=blur_radius)

        # Composite mask: dilate much more than feather so the feather gradient
        # falls fully INSIDE the inpainted region with no original bleed-through.
        mask_composite = _feather_mask(_dilate_mask(mask_raw_sd, radius=blur_radius * 4), radius=blur_radius)

        # Reference image for IP-Adapter
        ip_scale = input.ip_adapter_scale if input.ip_adapter_scale is not None else 0.6
        if input.reference_image_url:
            ref_sd = (await self.process_image_url(input.reference_image_url))\
                     .convert("RGB").resize((w, h), Image.LANCZOS)
            logger.info("Using custom reference image for IP-Adapter.")
        else:
            # Self-reference: use the ORIGINAL (unfilled) image so the CLIP
            # encoder captures authentic tone/style, not the mean-filled version.
            ref_sd   = _make_clean_reference(image_sd, mask_raw_sd)
            ip_scale = min(ip_scale, 0.25)
            logger.info(f"Self-reference mode — ip_scale capped at {ip_scale}.")

        pipe.set_ip_adapter_scale(ip_scale)

        logger.info(
            f"Inpainting {w}x{h} | steps={input.num_inference_steps} | "
            f"cfg={input.guidance_scale} | strength={input.strength} | "
            f"mask_blur={blur_radius} | ip_scale={ip_scale}"
        )

        generator = torch.Generator(device="cpu").manual_seed(42)
        with torch.inference_mode():
            raw_result = pipe(
                prompt=input.prompt,
                negative_prompt=input.negative_prompt,
                image=image_sd_fill,
                mask_image=mask_sd,
                ip_adapter_image=ref_sd,
                num_inference_steps=input.num_inference_steps,
                guidance_scale=input.guidance_scale,
                strength=input.strength,
                width=w,
                height=h,
                generator=generator,
            ).images[0]

        output_image = _composite_with_original(image_sd, raw_result, mask_composite)
        output_image = output_image.resize(original_size, Image.LANCZOS)

        self._debug_image(image_sd,      "inpaint_input")
        self._debug_image(image_sd_fill, "inpaint_input_filled")
        self._debug_image(mask_raw,      "inpaint_mask_raw")
        self._debug_image(mask_sd,       "inpaint_mask_soft")
        self._debug_image(ref_sd,        "inpaint_reference")
        self._debug_image(raw_result,    "inpaint_raw")
        self._debug_image(output_image,  "inpaint_output")

        return await self.save_image(output_image)
