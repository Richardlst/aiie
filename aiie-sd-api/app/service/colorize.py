import asyncio
import concurrent.futures
import gc
import os
import re
import sys
import time
import traceback
from typing import Any, Tuple

import PIL.Image
import numpy as np
import torch

os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "300"
os.environ["HF_HUB_ETAG_TIMEOUT"] = "60"
os.environ["HF_HUB_CHUNK_TIMEOUT"] = "60"

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
BASE_MODEL_ID         = os.path.abspath("models/realisticVisionV60B1_v51HyperVAE.safetensors") 
CONTROLNET_MODEL_PATH = os.path.abspath("models/controlnet_recolor")
CAPTION_MODEL_ID      = "Salesforce/blip-image-captioning-base"

BASE_MODEL_ID         = os.path.abspath("models/realisticVisionV60B1_v51HyperVAE.safetensors") 
CONTROLNET_MODEL_PATH = os.path.abspath("models/controlnet_recolor")
CAPTION_MODEL_ID      = "Salesforce/blip-image-captioning-base"

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
    "circa", "balck and white,", "monochrome,", "black-and-white,",
    "black-and-white photography,", "black - and - white photography,",
    "monochrome bw,", "black white,", "black an white,", "grainy footage,",
    "grainy footage", "grainy photo,", "grainy photo", "b&w photo",
    "back and white", "back and white,", "monochrome contrast", "monochrome",
    "grainy", "grainy photograph,", "grainy photograph", "low contrast,",
    "low contrast", "b & w", "grainy black-and-white photo,", "bw", "bw,",
    "grainy black-and-white photo", "b & w,", "b&w,", "b&w!,", "b&w",
    "black - and - white,", "bw photo,", "grainy  photo,", "black-and-white photo,",
    "black-and-white photo", "black - and - white photography", "b&w photo,",
    "monochromatic photo,", "grainy monochrome photo,", "monochromatic",
    "circa", "balck and white,", "monochrome,", "black-and-white,",
    "black-and-white photography,", "black - and - white photography,",
    "monochrome bw,", "black white,", "black an white,", "grainy footage,",
    "grainy footage", "grainy photo,", "grainy photo", "b&w photo",
    "back and white", "back and white,", "monochrome contrast", "monochrome",
    "grainy", "grainy photograph,", "grainy photograph", "low contrast,",
    "low contrast", "b & w", "grainy black-and-white photo,", "bw", "bw,",
    "grainy black-and-white photo", "b & w,", "b&w,", "b&w!,", "b&w",
    "black - and - white,", "bw photo,", "grainy  photo,", "black-and-white photo,",
    "black-and-white photo", "black - and - white photography", "b&w photo,",
    "monochromatic photo,", "grainy monochrome photo,", "monochromatic",
    "blurry photo,", "blurry,", "blurry photography,", "monochromatic photo",
    "black - and - white photograph,", "black - and - white photograph",
    "black on white,", "black on white", "black-and-white", "historical image,",
    "historical picture,", "historical photo,", "historical photograph,",
    "black on white,", "black on white", "black-and-white", "historical image,",
    "historical picture,", "historical photo,", "historical photograph,",
    "archival photo,", "taken in the early", "taken in the late",
    "taken in the", "historic photograph,", "restored,", "restored",
    "historical photo", "historical setting,", "historic photo,", "historic",
    "historical photo", "historical setting,", "historic photo,", "historic",
    "desaturated!!,", "desaturated!,", "desaturated,", "desaturated",
    "taken in", "shot on leica", "shot on leica sl2", "sl2",
    "taken with a leica camera", "leica sl2", "leica", "setting",
    "overcast day", "overcast weather", "slight overcast", "overcast",
    "picture taken in", "photo taken in", ", photo", ",  photo", ",   photo",
    ",    photo", ", photograph", ",,", ",,,", ",,,,", " ,", "  ,", "   ,", "    ,",
    "picture taken in", "photo taken in", ", photo", ",  photo", ",   photo",
    ",    photo", ", photograph", ",,", ",,,", ",,,,", " ,", "  ,", "   ,", "    ,",
]
_UNLIKELY_WORDS.extend(_a1 + _a2 + _a3 + _a4 + _b1 + _b2 + _b3 + _b4 + _MANUAL_WORDS)

_pipe = None
_caption_processor = None
_caption_model = None

def _get_or_load_pipeline():
    global _pipe, _caption_processor, _caption_model

    if _pipe is not None:
        return _pipe, _caption_processor, _caption_model

    from diffusers import (
        StableDiffusionControlNetPipeline, 
        StableDiffusionControlNetPipeline, 
        ControlNetModel,
        EulerAncestralDiscreteScheduler,
        EulerAncestralDiscreteScheduler,
    )
    from transformers import BlipProcessor, BlipForConditionalGeneration

    weight_dtype = torch.float16 if device == "cuda" else torch.float32

    if device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True

    logger.info("Loading ControlNet Recolor...")
    controlnet = ControlNetModel.from_pretrained(
        CONTROLNET_MODEL_PATH, 
        torch_dtype=weight_dtype
    )

    logger.info("Assembling SD 1.5 Txt2Img Pipeline...")
    pipe = StableDiffusionControlNetPipeline.from_single_file(
        BASE_MODEL_ID, 
        controlnet=controlnet,
    logger.info("Assembling SD 1.5 Txt2Img Pipeline...")
    pipe = StableDiffusionControlNetPipeline.from_single_file(
        BASE_MODEL_ID, 
        controlnet=controlnet,
        torch_dtype=weight_dtype,
        safety_checker=None
        safety_checker=None
    )
    
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

    if device == "cuda":
        pipe.enable_model_cpu_offload() 
        logger.info("Enabled model CPU offload.")
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception as e:
            pipe.enable_attention_slicing(slice_size=1)
        pipe.enable_model_cpu_offload() 
        logger.info("Enabled model CPU offload.")
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception as e:
            pipe.enable_attention_slicing(slice_size=1)
    else:
        pipe.to("cpu", dtype=torch.float32)

    pipe.enable_vae_slicing()
    if device == "cuda":
        pipe.enable_vae_tiling()

    logger.info("Loading BLIP captioning model...")
    logger.info("Loading BLIP captioning model...")
    _caption_processor = BlipProcessor.from_pretrained(CAPTION_MODEL_ID)
    _caption_model = BlipForConditionalGeneration.from_pretrained(
        CAPTION_MODEL_ID, torch_dtype=torch.float32,
    ).to("cpu").eval()

    _pipe = pipe
    return _pipe, _caption_processor, _caption_model

def _clean_caption(caption):
    for word in _UNLIKELY_WORDS:
        caption = caption.replace(word, "")
    caption = re.sub(r",\s*,+", ",", caption)
    caption = re.sub(r"\s{2,}", " ", caption)
    return caption.strip().strip(",").strip()

def _apply_color(grayscale_rgb, color_map, saturation_boost=1.35):
    # Khôi phục độ sáng từ ảnh gốc, lấy màu từ AI và cho phép tăng đậm màu (Saturation)
def _apply_color(grayscale_rgb, color_map, saturation_boost=1.35):
    # Khôi phục độ sáng từ ảnh gốc, lấy màu từ AI và cho phép tăng đậm màu (Saturation)
    grayscale_lab = grayscale_rgb.convert("LAB")
    color_map_lab = color_map.convert("LAB")

    l_channel, _, _ = grayscale_lab.split()
    _, a_channel, b_channel = color_map_lab.split()

    if saturation_boost != 1.0:
    if saturation_boost != 1.0:
        neutral = 128.0
        # Khuếch đại khoảng cách màu từ điểm trung tính (128)
        # Khuếch đại khoảng cách màu từ điểm trung tính (128)
        a_arr = np.array(a_channel, dtype=np.float64)
        b_arr = np.array(b_channel, dtype=np.float64)
        
        a_blended = (neutral + saturation_boost * (a_arr - neutral)).clip(0, 255).astype(np.uint8)
        b_blended = (neutral + saturation_boost * (b_arr - neutral)).clip(0, 255).astype(np.uint8)
        
        
        a_blended = (neutral + saturation_boost * (a_arr - neutral)).clip(0, 255).astype(np.uint8)
        b_blended = (neutral + saturation_boost * (b_arr - neutral)).clip(0, 255).astype(np.uint8)
        
        a_channel = PIL.Image.fromarray(a_blended, mode="L")
        b_channel = PIL.Image.fromarray(b_blended, mode="L")

    return PIL.Image.merge("LAB", (l_channel, a_channel, b_channel)).convert("RGB")

def _generate_caption(image, processor, model):
    with torch.inference_mode():
        inputs = processor(image, "a photography of", return_tensors="pt").to(
            "cpu", dtype=torch.float32,
        )
        caption_ids = model.generate(**inputs, max_new_tokens=50)

    raw_caption = processor.decode(caption_ids[0], skip_special_tokens=True)
    caption = _clean_caption(raw_caption)
    return caption

def _sync_colorize(input_params, image):
    try:
        if device == "cuda":
            gc.collect()
            torch.cuda.empty_cache()
def _sync_colorize(input_params, image):
    try:
        if device == "cuda":
            gc.collect()
            torch.cuda.empty_cache()

        pipe, processor, caption_model = _get_or_load_pipeline()
        pipe, processor, caption_model = _get_or_load_pipeline()

        original_size = image.size
        
        max_dim = getattr(input_params, "max_dimension", 768)
        if max(original_size) > max_dim:
            ratio = max_dim / max(original_size)
            new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
            new_size = (new_size[0] // 64 * 64, new_size[1] // 64 * 64)
            image = image.resize(new_size, PIL.Image.LANCZOS)
        else:
            new_size = (original_size[0] // 64 * 64, original_size[1] // 64 * 64)
            if new_size != original_size:
                image = image.resize(new_size, PIL.Image.LANCZOS)

        init_image = image.convert("L").convert("RGB")
        control_image = init_image.copy()

        semantic_caption = _generate_caption(image, processor, caption_model)
        user_prompt = (input_params.prompt or "").strip()
        
        # Thêm từ khóa "Kodak color film" và "vivid skin tones" giúp ảnh cũ lên màu có sức sống
        final_prompt = f"{semantic_caption}, Kodak color film, vivid skin tones, high quality, highly detailed, photorealistic. {user_prompt}"
        negative_prompt = "distorted, artifacts, oversaturated, neon, glowing"

        seed = getattr(input_params, "seed", -1)
        if seed == -1:
            seed = int(time.time()) % 100000
        generator = torch.Generator(device="cpu").manual_seed(seed)

        # Giữ nguyên độ an toàn của ControlNet Recolor
        safe_guidance_scale = 2.5
        original_size = image.size
        
        max_dim = getattr(input_params, "max_dimension", 768)
        if max(original_size) > max_dim:
            ratio = max_dim / max(original_size)
            new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
            new_size = (new_size[0] // 64 * 64, new_size[1] // 64 * 64)
            image = image.resize(new_size, PIL.Image.LANCZOS)
        else:
            new_size = (original_size[0] // 64 * 64, original_size[1] // 64 * 64)
            if new_size != original_size:
                image = image.resize(new_size, PIL.Image.LANCZOS)

        init_image = image.convert("L").convert("RGB")
        control_image = init_image.copy()

        semantic_caption = _generate_caption(image, processor, caption_model)
        user_prompt = (input_params.prompt or "").strip()
        
        # Thêm từ khóa "Kodak color film" và "vivid skin tones" giúp ảnh cũ lên màu có sức sống
        final_prompt = f"{semantic_caption}, Kodak color film, vivid skin tones, high quality, highly detailed, photorealistic. {user_prompt}"
        negative_prompt = "distorted, artifacts, oversaturated, neon, glowing"

        seed = getattr(input_params, "seed", -1)
        if seed == -1:
            seed = int(time.time()) % 100000
        generator = torch.Generator(device="cpu").manual_seed(seed)

        # Giữ nguyên độ an toàn của ControlNet Recolor
        safe_guidance_scale = 2.5

        with torch.inference_mode():
            result = pipe(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                image=control_image,
                controlnet_conditioning_scale=1.0,
                num_inference_steps=input_params.num_inference_steps,
                guidance_scale=safe_guidance_scale,
                generator=generator,
            )
        with torch.inference_mode():
            result = pipe(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                image=control_image,
                controlnet_conditioning_scale=1.0,
                num_inference_steps=input_params.num_inference_steps,
                guidance_scale=safe_guidance_scale,
                generator=generator,
            )

        # Bơm thêm 35% độ đậm màu (saturation_boost = 1.35) để ảnh rực rỡ hơn
        color_intensity = getattr(input_params, "color_intensity", 1.0)
        final_saturation = 1.35 * color_intensity

        colorized = _apply_color(
            init_image,
            result.images[0],
            saturation_boost=final_saturation,
        ).resize(original_size, PIL.Image.LANCZOS)
        # Bơm thêm 35% độ đậm màu (saturation_boost = 1.35) để ảnh rực rỡ hơn
        color_intensity = getattr(input_params, "color_intensity", 1.0)
        final_saturation = 1.35 * color_intensity

        colorized = _apply_color(
            init_image,
            result.images[0],
            saturation_boost=final_saturation,
        ).resize(original_size, PIL.Image.LANCZOS)

        del result
        if device == "cuda":
            torch.cuda.empty_cache()
        del result
        if device == "cuda":
            torch.cuda.empty_cache()

        return colorized
        return colorized

    except Exception as e:
        logger.error(f"💥 LỖI TẠI LÕI AI (RENDER):\n{traceback.format_exc()}")
        raise e
    except Exception as e:
        logger.error(f"💥 LỖI TẠI LÕI AI (RENDER):\n{traceback.format_exc()}")
        raise e

class ColorizeService(BaseSDService):
    async def run(self, input_params):
        try:
            image = await self.process_image_url(input_params.image_url)
            loop = asyncio.get_event_loop()
            try:
                colorized = await asyncio.wait_for(
                    loop.run_in_executor(
                        _EXECUTOR,
                        _sync_colorize,
                        input_params,
                        image,
                    ),
                    timeout=600
                )
            except asyncio.TimeoutError:
                raise RuntimeError("Colorization process timed out.")

            self._debug_image(colorized, "colorized")
            return await self.save_image(colorized)
            
        except Exception as e:
            logger.error(f"🔥 LỖI CỰC NGHIÊM TRỌNG BỊ ẨN:\n{traceback.format_exc()}")
            raise e
            self._debug_image(colorized, "colorized")
            return await self.save_image(colorized)
            
        except Exception as e:
            logger.error(f"🔥 LỖI CỰC NGHIÊM TRỌNG BỊ ẨN:\n{traceback.format_exc()}")
            raise e