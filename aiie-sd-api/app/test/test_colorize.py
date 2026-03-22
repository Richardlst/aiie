"""
Batch colorization test — processes all grayscale/B&W images in *input_dir*
and writes colourised results to *output_dir/<timestamp>/*.

Memory-optimised: SDXL uses CPU-offload (peak ~3 GB VRAM instead of ~7 GB),
BLIP captioning runs entirely on CPU.

Usage (from the aiie-sd-api root):
    python -m app.test.test_colorize
"""

import gc
import os
import re
import glob
import torch
import numpy as np
import PIL.Image
from datetime import datetime
from tqdm import tqdm

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

from app.models import ColorizeRequest
from app.settings import settings

# ── Setup ────────────────────────────────────────────────────────────────────
device = settings.DEVICE
weight_dtype = torch.float16 if device == "cuda" else torch.float32

input_dir = "input_images"        # Directory containing B&W / grayscale images
output_dir = "eval/colorize"      # Root output directory

CONTROL_SIZE = 512

# Model identifiers
BASE_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
CONTROLNET_REPO = "nickpai/sdxl_light_caption_output"
CONTROLNET_LOCAL_DIR = "sdxl_light_caption_output"
CONTROLNET_SUBDIR = os.path.join(CONTROLNET_LOCAL_DIR, "checkpoint-30000", "controlnet")
LIGHTNING_REPO = "ByteDance/SDXL-Lightning"
LIGHTNING_FILE = "sdxl_lightning_8step_unet.safetensors"
CAPTION_MODEL_ID = "Salesforce/blip-image-captioning-large"

# Words to strip from BLIP captions — ported from fffiloni/text-guided-image-colorization
_UNLIKELY_WORDS: list[str] = []

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

# Default request configuration
config = ColorizeRequest(
    image_url="dummy_url",
    prompt="",
    negative_prompt=(
        "low quality, bad quality, low contrast, black and white, bw, monochrome, "
        "grainy, blurry, historical, restored, desaturate"
    ),
    num_inference_steps=8,
    guidance_scale=7.5,
    color_intensity=1.0,
    seed=123,
    append_caption=True,
)


# ── Helper functions ─────────────────────────────────────────────────────────

def clean_caption(caption: str) -> str:
    """Remove B&W-related words BLIP tends to inject."""
    for w in _UNLIKELY_WORDS:
        caption = caption.replace(w, "")
    caption = re.sub(r",\s*,+", ",", caption)
    caption = re.sub(r"\s{2,}", " ", caption)
    return caption.strip().strip(",").strip()


def apply_color(
    grayscale_rgb: PIL.Image.Image,
    color_map: PIL.Image.Image,
    intensity: float = 1.0,
) -> PIL.Image.Image:
    """Merge L from *grayscale_rgb* with AB from *color_map* in LAB space."""
    grayscale_lab = grayscale_rgb.convert("LAB")
    color_lab = color_map.convert("LAB")

    l_ch, _, _ = grayscale_lab.split()
    _, a_ch, b_ch = color_lab.split()

    if intensity < 1.0:
        neutral = 128.0
        a_arr = np.array(a_ch, dtype=np.float64)
        b_arr = np.array(b_ch, dtype=np.float64)
        a_ch = PIL.Image.fromarray(
            (neutral + intensity * (a_arr - neutral)).clip(0, 255).astype(np.uint8),
            mode="L",
        )
        b_ch = PIL.Image.fromarray(
            (neutral + intensity * (b_arr - neutral)).clip(0, 255).astype(np.uint8),
            mode="L",
        )

    return PIL.Image.merge("LAB", (l_ch, a_ch, b_ch)).convert("RGB")


def process_image(
    image_path: str,
    output_path: str,
    pipe,
    caption_processor,
    caption_model,
    cfg: ColorizeRequest,
) -> bool:
    """Colorize a single image and save the result."""
    try:
        image = PIL.Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        original_size = image.size
        control_image = image.convert("L").convert("RGB").resize((CONTROL_SIZE, CONTROL_SIZE))

        # Build prompt — BLIP runs on CPU
        user_prompt = (cfg.prompt or "").strip()
        if not user_prompt or cfg.append_caption:
            with torch.inference_mode():
                inputs = caption_processor(
                    image, "a photography of", return_tensors="pt"
                ).to("cpu", dtype=torch.float32)
                caption_ids = caption_model.generate(**inputs, max_new_tokens=50)
            caption = caption_processor.decode(caption_ids[0], skip_special_tokens=True)
            caption = clean_caption(caption)
            print(f"  BLIP caption: {caption}")
            final_prompt = f"{user_prompt}, {caption}" if user_prompt else caption
        else:
            final_prompt = user_prompt

        negative_prompt = cfg.negative_prompt or ""
        print(f"  Prompt: {final_prompt}")

        # Inference — generator on CPU for compatibility with cpu_offload
        generator = torch.Generator(device="cpu").manual_seed(cfg.seed)
        with torch.inference_mode():
            result = pipe(
                prompt=[final_prompt],
                negative_prompt=[negative_prompt],
                num_inference_steps=cfg.num_inference_steps,
                guidance_scale=cfg.guidance_scale,
                generator=generator,
                image=control_image,
            )

        # Post-process
        colorized = apply_color(
            control_image, result.images[0], intensity=cfg.color_intensity
        ).resize(original_size, PIL.Image.LANCZOS)

        # Free result tensors early
        del result
        if device == "cuda":
            torch.cuda.empty_cache()

        colorized.save(output_path)
        return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Free VRAM
    if device == "cuda":
        torch.cuda.empty_cache()
        gc.collect()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(output_dir, timestamp)
    os.makedirs(run_dir, exist_ok=True)

    print(f"Input:  {input_dir}")
    print(f"Output: {run_dir}")
    print(f"Device: {device}  dtype: {weight_dtype}")

    # ── Load pipeline ────────────────────────────────────────────────────────
    print("\n=== Loading models (memory-optimised) ===")

    print("  Downloading ControlNet snapshot…")
    snapshot_download(repo_id=CONTROLNET_REPO, local_dir=CONTROLNET_LOCAL_DIR)

    print("  Loading VAE…")
    vae = AutoencoderKL.from_pretrained(
        BASE_MODEL_ID, subfolder="vae", torch_dtype=weight_dtype,
    )

    print("  Loading UNet (SDXL-Lightning)…")
    unet = UNet2DConditionModel.from_config(BASE_MODEL_ID, subfolder="unet")
    unet.load_state_dict(
        load_file(hf_hub_download(LIGHTNING_REPO, LIGHTNING_FILE))
    )

    print("  Loading ControlNet…")
    controlnet = ControlNetModel.from_pretrained(CONTROLNET_SUBDIR, torch_dtype=weight_dtype)

    print("  Assembling SDXL-ControlNet pipeline…")
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        BASE_MODEL_ID, vae=vae, unet=unet, controlnet=controlnet,
        torch_dtype=weight_dtype,
    )
    pipe.scheduler = EulerDiscreteScheduler.from_config(
        pipe.scheduler.config, timestep_spacing="trailing",
    )
    pipe.safety_checker = None

    # Memory optimisations — CPU offload keeps only one sub-model on GPU at a time
    if device == "cuda":
        pipe.enable_model_cpu_offload()
        print("  ✓ Model CPU offload enabled — peak VRAM ≈ 3-4 GB instead of ~7 GB")
    else:
        pipe.to("cpu", dtype=torch.float32)

    pipe.enable_attention_slicing(slice_size="auto")
    pipe.enable_vae_slicing()
    if device == "cuda":
        pipe.enable_vae_tiling()

    # BLIP stays on CPU — fast enough for captioning, saves all VRAM for SDXL
    print("  Loading BLIP captioning model (CPU-only)…")
    caption_processor = BlipProcessor.from_pretrained(CAPTION_MODEL_ID)
    caption_model = BlipForConditionalGeneration.from_pretrained(
        CAPTION_MODEL_ID, torch_dtype=torch.float32,
    ).to("cpu").eval()

    print("  Pipeline ready.\n")

    # ── Discover images ──────────────────────────────────────────────────────
    extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))

    if not image_files:
        print(f"No images found in {input_dir}")
    else:
        print(f"Found {len(image_files)} image(s)\n")

        successful = 0
        failed = 0

        for img_path in tqdm(image_files, desc="Colorizing"):
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            out_path = os.path.join(run_dir, f"{base_name}.png")

            print(f"\nProcessing: {img_path}")
            ok = process_image(
                img_path, out_path, pipe, caption_processor, caption_model, config,
            )
            if ok:
                successful += 1
            else:
                failed += 1

        print(f"\nDone! Success: {successful}  Failed: {failed}")

    # ── Cleanup ──────────────────────────────────────────────────────────────
    del pipe, caption_model, caption_processor
    if device == "cuda":
        torch.cuda.empty_cache()
        gc.collect()
