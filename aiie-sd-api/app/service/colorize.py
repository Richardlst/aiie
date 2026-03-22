import asyncio
import concurrent.futures
import gc
import os
import re
from typing import Any, Tuple

import PIL.Image
import numpy as np

_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="colorize")

from app.models import ColorizeRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("ColorizeService")
device = settings.DEVICE

# ---------------------------------------------------------------------------
# Model identifiers
# ---------------------------------------------------------------------------
BASE_MODEL_ID        = "stabilityai/stable-diffusion-xl-base-1.0"
LIGHTNING_REPO       = "ByteDance/SDXL-Lightning"
LIGHTNING_FILE       = "sdxl_lightning_4step_unet.safetensors"
CONTROLNET_REPO      = "nickpai/sdxl_light_caption_output"
CONTROLNET_LOCAL_DIR = "sdxl_light_caption_output"
CONTROLNET_SUBDIR    = "sdxl_light_caption_output/checkpoint-30000/controlnet"
CAPTION_MODEL_ID     = "Salesforce/blip-image-captioning-base"
CONTROL_SIZE         = 1024

DEFAULT_NEGATIVE_PROMPT = (
    "low quality, bad quality, low contrast, black and white, bw, monochrome, "
    "grainy, blurry, historical, restored, desaturate"
)

# ---------------------------------------------------------------------------
# Words/phrases to strip from auto-generated captions.
# ---------------------------------------------------------------------------
_UNLIKELY_WORDS = []

_a1 = [f"{i}s" for i in range(1900, 2000)]
_a2 = [f"{i}" for i in range(1900, 2000)]
_a3 = [f"year {i}" for i in range(1900, 2000)]
_a4 = [f"circa {i}" for i in range(1900, 2000)]
_b1 = [f"{y[0]} {y[1]} {y[2]} {y[3]} s" for y in _a1]
_b2 = [f"{y[0]} {y[1]} {y[2]} {y[3]}" for y in _a1]
_b3 = [f"year {y[0]} {y[1]} {y[2]} {y[3]}" for y in _a1]
_b4 = [f"circa {y[0]} {y[1]} {y[2]} {y[3]}" for y in _a1]

_MANUAL_WORDS = [
    "black and white,", "black and white", "black & white,", "black & white",
    "circa", "balck and white,", "monochrome,",
    "black-and-white,", "black-and-white photography,",
    "black - and - white photography,", "monochrome bw,",
    "black white,", "black an white,",
    "grainy footage,", "grainy footage", "grainy photo,", "grainy photo",
    "b&w photo", "back and white", "back and white,",
    "monochrome contrast", "monochrome", "grainy",
    "grainy photograph,", "grainy photograph", "low contrast,", "low contrast",
    "b & w", "grainy black-and-white photo,", "bw", "bw,",
    "grainy black-and-white photo",
    "b & w,", "b&w,", "b&w!,", "b&w",
    "black - and - white,", "bw photo,", "grainy  photo,",
    "black-and-white photo,", "black-and-white photo",
    "black - and - white photography",
    "b&w photo,", "monochromatic photo,", "grainy monochrome photo,",
    "monochromatic",
    "blurry photo,", "blurry,", "blurry photography,", "monochromatic photo",
    "black - and - white photograph,", "black - and - white photograph",
    "black on white,", "black on white", "black-and-white",
    "historical image,", "historical picture,",
    "historical photo,", "historical photograph,",
    "archival photo,", "taken in the early", "taken in the late",
    "taken in the", "historic photograph,", "restored,", "restored",
    "historical photo", "historical setting,",
    "historic photo,", "historic",
    "desaturated!!,", "desaturated!,", "desaturated,", "desaturated",
    "taken in", "shot on leica", "shot on leica sl2", "sl2",
    "taken with a leica camera", "leica sl2", "leica", "setting",
    "overcast day", "overcast weather", "slight overcast", "overcast",
    "picture taken in", "photo taken in",
    ", photo", ",  photo", ",   photo", ",    photo", ", photograph",
    ",,", ",,,", ",,,,", " ,", "  ,", "   ,", "    ,",
]

_UNLIKELY_WORDS.extend(_a1 + _a2 + _a3 + _a4 + _b1 + _b2 + _b3 + _b4 + _MANUAL_WORDS)

# ---------------------------------------------------------------------------
# Module-level cache
# ---------------------------------------------------------------------------
_pipe = None
_caption_processor = None
_caption_model = None


def _get_or_load_pipeline():
    global _pipe, _caption_processor, _caption_model

    if _pipe is not None:
        return _pipe, _caption_processor, _caption_model

    import torch
    from diffusers import (
        StableDiffusionXLControlNetPipeline,
        ControlNetModel,
        EulerDiscreteScheduler,
        UNet2DConditionModel,
        AutoencoderKL,
    )
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from safetensors.torch import load_file
    from huggingface_hub import hf_hub_download, snapshot_download

    _num_threads = max(1, (os.cpu_count() or 4) // 2)
    torch.set_num_threads(_num_threads)
    torch.set_num_interop_threads(max(1, _num_threads // 2))

    weight_dtype = torch.float16 if device == "cuda" else torch.float32

    if device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True

    logger.info(f"Ensuring ControlNet snapshot ({CONTROLNET_REPO})...")
    snapshot_download(repo_id=CONTROLNET_REPO, local_dir=CONTROLNET_LOCAL_DIR)

    logger.info("Loading VAE...")
    vae = AutoencoderKL.from_pretrained(
        BASE_MODEL_ID, subfolder="vae", torch_dtype=weight_dtype,
    )

    logger.info("Loading UNet from SDXL-Lightning...")
    unet_config = UNet2DConditionModel.load_config(BASE_MODEL_ID, subfolder="unet")
    unet = UNet2DConditionModel.from_config(unet_config)
    unet.load_state_dict(
        load_file(hf_hub_download(LIGHTNING_REPO, LIGHTNING_FILE))
    )
    unet = unet.to(dtype=weight_dtype)

    logger.info("Loading ControlNet...")
    controlnet = ControlNetModel.from_pretrained(CONTROLNET_SUBDIR, torch_dtype=weight_dtype)

    logger.info("Assembling SDXL-ControlNet pipeline...")
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        BASE_MODEL_ID, vae=vae, unet=unet, controlnet=controlnet,
        torch_dtype=weight_dtype,
    )
    pipe.scheduler = EulerDiscreteScheduler.from_config(
        pipe.scheduler.config, timestep_spacing="trailing",
    )
    pipe.safety_checker = None

    if device == "cuda":
        pipe.enable_model_cpu_offload()
        logger.info("Enabled model CPU offload (peak VRAM ~3 GB).")
        # NOTE: xformers is intentionally NOT enabled here.
        # enable_xformers_memory_efficient_attention() + enable_model_cpu_offload()
        # causes a process crash (WinError 10054).
    else:
        pipe.to("cpu", dtype=torch.float32)

    pipe.enable_attention_slicing(slice_size=1)
    pipe.enable_vae_slicing()
    if device == "cuda":
        pipe.enable_vae_tiling()

    logger.info("Loading BLIP captioning model (CPU-only)...")
    _caption_processor = BlipProcessor.from_pretrained(CAPTION_MODEL_ID)
    _caption_model = BlipForConditionalGeneration.from_pretrained(
        CAPTION_MODEL_ID, torch_dtype=torch.float32,
    ).to("cpu").eval()

    _pipe = pipe
    logger.info("Colorize pipeline ready (SDXL-Lightning + ControlNet).")
    return _pipe, _caption_processor, _caption_model


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_caption(caption):
    for word in _UNLIKELY_WORDS:
        caption = caption.replace(word, "")
    caption = re.sub(r",\s*,+", ",", caption)
    caption = re.sub(r"\s{2,}", " ", caption)
    return caption.strip().strip(",").strip()


def _apply_color(grayscale_rgb, color_map, intensity=1.0):
    grayscale_lab = grayscale_rgb.convert("LAB")
    color_map_lab = color_map.convert("LAB")

    l_channel, _, _ = grayscale_lab.split()
    _, a_channel, b_channel = color_map_lab.split()

    if intensity < 1.0:
        neutral = 128.0
        a_arr = np.array(a_channel, dtype=np.float64)
        b_arr = np.array(b_channel, dtype=np.float64)
        a_blended = (neutral + intensity * (a_arr - neutral)).clip(0, 255).astype(np.uint8)
        b_blended = (neutral + intensity * (b_arr - neutral)).clip(0, 255).astype(np.uint8)
        a_channel = PIL.Image.fromarray(a_blended, mode="L")
        b_channel = PIL.Image.fromarray(b_blended, mode="L")

    return PIL.Image.merge("LAB", (l_channel, a_channel, b_channel)).convert("RGB")


def _generate_caption(image, processor, model):
    import torch
    with torch.inference_mode():
        inputs = processor(image, "a photography of", return_tensors="pt").to(
            "cpu", dtype=torch.float32,
        )
        caption_ids = model.generate(**inputs, max_new_tokens=50)

    raw_caption = processor.decode(caption_ids[0], skip_special_tokens=True)
    caption = _clean_caption(raw_caption)
    logger.info(f"BLIP caption: {raw_caption!r} -> cleaned: {caption!r}")
    return caption


# ---------------------------------------------------------------------------
# Core service
# ---------------------------------------------------------------------------

def _sync_colorize(input, image):
    import torch

    if device == "cuda":
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        gc.collect()
        torch.cuda.empty_cache()
        logger.info(
            f"VRAM before colorize: "
            f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB allocated, "
            f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB reserved"
        )

    pipe, processor, caption_model = _get_or_load_pipeline()

    original_size = image.size
    logger.info(f"Original image size: {original_size}")

    control_image = image.convert("L").convert("RGB").resize(
        (CONTROL_SIZE, CONTROL_SIZE), PIL.Image.LANCZOS
    )

    user_prompt = (input.prompt or "").strip()
    if not user_prompt:
        logger.info("No user prompt -- generating auto-caption with BLIP...")
        final_prompt = _generate_caption(image, processor, caption_model)
    elif input.append_caption:
        caption = _generate_caption(image, processor, caption_model)
        final_prompt = f"{user_prompt}, {caption}"
    else:
        final_prompt = user_prompt

    negative_prompt = input.negative_prompt or DEFAULT_NEGATIVE_PROMPT
    logger.info(f"Colorizing -- prompt: {final_prompt!r}")

    generator = torch.Generator(device="cpu").manual_seed(input.seed)

    with torch.inference_mode():
        result = pipe(
            prompt=[final_prompt],
            negative_prompt=[negative_prompt],
            num_inference_steps=input.num_inference_steps,
            guidance_scale=input.guidance_scale,
            generator=generator,
            image=control_image,
        )

    colorized = _apply_color(
        control_image,
        result.images[0],
        intensity=input.color_intensity,
    ).resize(original_size, PIL.Image.LANCZOS)

    del result
    if device == "cuda":
        torch.cuda.empty_cache()

    logger.info("Colorization complete.")
    return colorized


class ColorizeService(BaseSDService):
    async def run(self, input):
        image = await self.process_image_url(input.image_url)

        control_preview = image.convert("L").convert("RGB").resize(
            (CONTROL_SIZE, CONTROL_SIZE), PIL.Image.LANCZOS
        )
        self._debug_image(control_preview, "control_image")

        loop = asyncio.get_event_loop()
        colorized = await loop.run_in_executor(
            _EXECUTOR,
            _sync_colorize,
            input,
            image,
        )

        self._debug_image(colorized, "colorized")
        return await self.save_image(colorized)