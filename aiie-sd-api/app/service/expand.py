import gc
import traceback
from typing import Optional

import numpy as np
import torch
from PIL import Image, ImageFilter
from diffusers import StableDiffusionInpaintPipeline, EulerAncestralDiscreteScheduler
from fastapi import HTTPException

from app.models import ExpandRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("ExpandService")
device = settings.DEVICE

MODEL_ID = "./models/realisticVisionV60B1_v51HyperInpaintVAE.safetensors"

_pipe_cache: Optional[StableDiffusionInpaintPipeline] = None

def _load_pipe() -> StableDiffusionInpaintPipeline:
    global _pipe_cache
    if _pipe_cache is not None:
        return _pipe_cache

    logger.info(f"Loading expand pipeline ({MODEL_ID})...")
    torch_dtype = torch.float16 if device == "cuda" else torch.float32

    pipe = StableDiffusionInpaintPipeline.from_single_file(
        MODEL_ID,
        torch_dtype=torch_dtype,
        safety_checker=None,
    )

    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.vae.enable_slicing()
    pipe.enable_attention_slicing(slice_size="auto")

    if device == "cuda":
        pipe.enable_model_cpu_offload()
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception as e:
            logger.warning(f"xformers error: {e}")
    else:
        pipe.to("cpu")

    _pipe_cache = pipe
    return pipe


class ExpandService(BaseSDService):
    def _scale_to_fit(self, image: Image.Image, input: ExpandRequest, max_orig: int = 512) -> Image.Image:
        w, h = image.size
        bigger = max(w, h)
        if bigger <= max_orig:
            return image
        scale = max_orig / bigger
        
        image = image.resize((int(w * scale) // 8 * 8, int(h * scale) // 8 * 8), Image.LANCZOS)
        input.expand_left   = int(input.expand_left   * scale)
        input.expand_right  = int(input.expand_right  * scale)
        input.expand_top    = int(input.expand_top    * scale)
        input.expand_bottom = int(input.expand_bottom * scale)
        return image

    async def run(self, input: ExpandRequest) -> str:
        try:
            if device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()

            pipe = _load_pipe()
            image = await self.process_image_url(input.image_url)
            image = image.convert("RGB")
            
            image = self._scale_to_fit(image, input)
            orig_w, orig_h = image.size

            el = max(0, input.expand_left)  // 8 * 8
            er = max(0, input.expand_right) // 8 * 8
            et = max(0, input.expand_top)   // 8 * 8
            eb = max(0, input.expand_bottom)// 8 * 8

            canvas_w = orig_w + el + er
            canvas_h = orig_h + et + eb

            # --- BƯỚC 1: Kỹ thuật Blurry Reflect (Khớp Tone Màu & Ánh Sáng 100%) ---
            arr = np.array(image)
            # Phản chiếu ảnh để lấy dải màu chính xác của môi trường xung quanh
            reflected_arr = np.pad(arr, ((et, eb), (el, er), (0, 0)), mode="reflect")
            canvas_image = Image.fromarray(reflected_arr)
            
            # BÍ QUYẾT: Làm mờ cực mạnh để xóa sạch các hình thù lộn ngược, chỉ giữ lại "Màu sắc" và "Ánh sáng"
            blurred_canvas = canvas_image.filter(ImageFilter.GaussianBlur(radius=64))
            
            # Dán ảnh thật sắc nét vào chính giữa dải màu đã được làm mờ
            canvas_image = blurred_canvas.copy()
            canvas_image.paste(image, (el, et))

            # --- BƯỚC 2: Tạo Mask AI ---
            mask = Image.new("L", (canvas_w, canvas_h), 255)
            # Lùi vào 8 pixel để AI vẽ khớp nối với viền ảnh thật
            mask.paste(0, (el + 8, et + 8, el + orig_w - 8, et + orig_h - 8))
            
            # Giảm radius xuống 8. Vì nền đã mờ, mask sắc nét giúp AI định hình vùng vẽ tốt hơn
            mask_for_ai = mask.filter(ImageFilter.GaussianBlur(radius=8))

            # --- BƯỚC 3: Cấu hình & Sinh ảnh ---
            prompt = input.prompt or (
                "high resolution photograph, seamless continuation, "
                "detailed texture, sharp focus, intricate details, matching lighting"
            )
            negative_prompt = input.negative_prompt or (
                "visible seams, blurry, low quality, distorted, mirror effect, watermark"
            )

            # Truncate prompts to stay within token limit (77 tokens max)
            prompt = self._truncate_prompt(prompt, max_tokens=77)
            negative_prompt = self._truncate_prompt(negative_prompt, max_tokens=77)

            # ĐIỀU CHỈNH QUAN TRỌNG: Nâng Strength lên 0.90
            # Nền ở Bước 1 đang mờ tịt, ta cần ép AI vẽ mới gần như hoàn toàn để tạo chi tiết nét,
            # AI sẽ tự động "hút" dải màu từ nền mờ đó để phối màu cho chuẩn.
            actual_strength = 0.90 
            actual_steps = 30 # Tăng số bước lên 30 để AI có đủ thời gian vẽ chi tiết sắc sảo
            actual_cfg = 7.5

            max_sd_dim = 1024 
            scale = min(1.0, max_sd_dim / max(canvas_w, canvas_h))
            sd_w, sd_h = int(canvas_w * scale) // 8 * 8, int(canvas_h * scale) // 8 * 8

            canvas_sd = canvas_image.resize((sd_w, sd_h), Image.LANCZOS)
            mask_sd = mask_for_ai.resize((sd_w, sd_h), Image.LANCZOS)

            generator = torch.Generator(device=device).manual_seed(42)

            with torch.inference_mode():
                result_sd = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=canvas_sd,
                    mask_image=mask_sd,
                    num_inference_steps=actual_steps,
                    guidance_scale=actual_cfg,
                    strength=actual_strength, 
                    width=sd_w,
                    height=sd_h,
                    generator=generator,
                ).images[0]

            final_result = result_sd.resize((canvas_w, canvas_h), Image.LANCZOS)

            # --- BƯỚC 4: Hòa trộn Micro-Feathering ---
            original_canvas = Image.new("RGB", (canvas_w, canvas_h))
            original_canvas.paste(image, (el, et))
            
            final_mask = Image.new("L", (canvas_w, canvas_h), 0)
            final_mask.paste(255, (el + 4, et + 4, el + orig_w - 4, et + orig_h - 4))
            
            # Mask cắt cực mỏng (Radius=2) để không tạo vệt sương mờ
            final_mask = final_mask.filter(ImageFilter.GaussianBlur(radius=2))
            
            # Trộn lại
            final_result = Image.composite(original_canvas, final_result, final_mask)

            return await self.save_image(final_result)

        except Exception as e:
            logger.error(f"Expand failed: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))