import gc
from typing import Any, Optional

import numpy as np
import torch
from PIL import Image, ImageFilter
from diffusers import StableDiffusionInpaintPipeline, EulerAncestralDiscreteScheduler
from diffusers import StableDiffusionInpaintPipeline, EulerAncestralDiscreteScheduler

from app.models import InpaintRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("InpaintService")
device = settings.DEVICE

# Sử dụng model Hyper Inpaint chuyên dụng
BASE_MODEL_ID        = "./models/realisticVisionV60B1_v51HyperInpaintVAE.safetensors"
# Sử dụng model Hyper Inpaint chuyên dụng
BASE_MODEL_ID        = "./models/realisticVisionV60B1_v51HyperInpaintVAE.safetensors"
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

    logger.info("Loading SD inpaint pipeline…")
    pipe = StableDiffusionInpaintPipeline.from_single_file(
    pipe = StableDiffusionInpaintPipeline.from_single_file(
        BASE_MODEL_ID,
        torch_dtype=torch_dtype,
        safety_checker=None,
    )

    # Đổi sang Euler A cho model Hyper/Turbo để ảnh mượt mà hơn ở steps thấp
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    # Đổi sang Euler A cho model Hyper/Turbo để ảnh mượt mà hơn ở steps thấp
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.vae.enable_slicing()

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
    """Mở rộng vùng trắng của mask"""
    """Mở rộng vùng trắng của mask"""
    if radius <= 0:
        return mask
    kernel = 2 * radius + 1
    return mask.filter(ImageFilter.MaxFilter(kernel))


def _feather_mask(mask: Image.Image, radius: int) -> Image.Image:
    """Làm mờ viền mask để trộn ảnh mượt hơn"""
    """Làm mờ viền mask để trộn ảnh mượt hơn"""
    if radius <= 0:
        return mask
    return mask.filter(ImageFilter.GaussianBlur(radius=radius))


def _composite_with_original(
    original: Image.Image,
    inpainted: Image.Image,
    mask: Image.Image,
) -> Image.Image:
    """Ghép vùng ảnh mới tạo vào ảnh gốc dựa trên mask"""
    """Ghép vùng ảnh mới tạo vào ảnh gốc dựa trên mask"""
    orig_np = np.array(original.convert("RGB"), dtype=np.float32)
    inp_np  = np.array(inpainted.convert("RGB"), dtype=np.float32)
    msk_np  = np.array(mask.convert("L"), dtype=np.float32)[:, :, None] / 255.0
    blended = inp_np * msk_np + orig_np * (1.0 - msk_np)
    return Image.fromarray(blended.clip(0, 255).astype(np.uint8))


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

        blur_radius = input.mask_blur_radius if input.mask_blur_radius is not None else 16
        blur_radius = input.mask_blur_radius if input.mask_blur_radius is not None else 16

        w = image.width  // 8 * 8
        h = image.height // 8 * 8
        image_sd    = image.resize((w, h), Image.LANCZOS)
        mask_raw_sd = mask_raw.resize((w, h), Image.LANCZOS)

        # Xử lý mask - KHÔNG điền màu xám, chỉ làm mờ (feather) và mở rộng (dilate)
        fill_mask = _dilate_mask(mask_raw_sd, radius=blur_radius + 4)
        mask_sd = _feather_mask(fill_mask, radius=blur_radius + 2)
        # Xử lý mask - KHÔNG điền màu xám, chỉ làm mờ (feather) và mở rộng (dilate)
        fill_mask = _dilate_mask(mask_raw_sd, radius=blur_radius + 4)
        mask_sd = _feather_mask(fill_mask, radius=blur_radius + 2)
        mask_composite = _feather_mask(_dilate_mask(mask_raw_sd, radius=blur_radius * 4), radius=blur_radius)

        # Reference image for IP-Adapter
        ip_scale = input.ip_adapter_scale if input.ip_adapter_scale is not None else 0.6
        if input.reference_image_url:
            ref_sd = (await self.process_image_url(input.reference_image_url))\
                     .convert("RGB").resize((w, h), Image.LANCZOS)
            logger.info("Using custom reference image for IP-Adapter.")
        else:
            # Truyền thẳng ảnh gốc vào, IP-Adapter sẽ tự phân tích màu da/style
            ref_sd = image_sd
            # Truyền thẳng ảnh gốc vào, IP-Adapter sẽ tự phân tích màu da/style
            ref_sd = image_sd
            ip_scale = min(ip_scale, 0.25)
            logger.info(f"Self-reference mode — ip_scale capped at {ip_scale}.")

        pipe.set_ip_adapter_scale(ip_scale)

        # Rút gọn prompt, chỉ giữ các từ khóa làm nét và tự nhiên để tránh lỗi > 77 tokens
        prompt = input.prompt or (
            "flawless restoration, highly detailed skin texture, natural appearance, "
            "perfectly blended edges, cinematic lighting, 8k resolution, raw photo"
        )
        negative_prompt = input.negative_prompt or (
            "visible seams, dark spots, shadows, obvious patches, artificial, "
            "watermark, text, blurry, bad anatomy, deformed, rough edges, pixelated"
        )

        # Truncate prompts to stay within token limit (77 tokens max)
        prompt = self._truncate_prompt(prompt, max_tokens=77)
        negative_prompt = self._truncate_prompt(negative_prompt, max_tokens=77)

        # 🟢 BỘ LỌC THÔNG SỐ: Ép cấu hình dành riêng cho model HYPER/LIGHTNING
        actual_steps = 6 if input.num_inference_steps > 10 else input.num_inference_steps
        actual_cfg = 1.5 if input.guidance_scale > 3.0 else input.guidance_scale

        logger.info(
            f"Inpainting {w}x{h} | steps={actual_steps} | "
            f"cfg={actual_cfg} | strength={input.strength} | "
            f"Inpainting {w}x{h} | steps={actual_steps} | "
            f"cfg={actual_cfg} | strength={input.strength} | "
            f"mask_blur={blur_radius} | ip_scale={ip_scale}"
        )

        generator = torch.Generator(device="cpu").manual_seed(42)
        
        
        with torch.inference_mode():
            raw_result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=image_sd,         # 🟢 Truyền ảnh gốc, mô hình inpaint rất cần cái này
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=image_sd,         # 🟢 Truyền ảnh gốc, mô hình inpaint rất cần cái này
                mask_image=mask_sd,
                ip_adapter_image=ref_sd, 
                num_inference_steps=actual_steps,
                guidance_scale=actual_cfg,
                ip_adapter_image=ref_sd, 
                num_inference_steps=actual_steps,
                guidance_scale=actual_cfg,
                strength=input.strength,
                width=w,
                height=h,
                generator=generator,
            ).images[0]

        # Ghép vùng inpaint thành công vào ảnh gốc
        # Ghép vùng inpaint thành công vào ảnh gốc
        output_image = _composite_with_original(image_sd, raw_result, mask_composite)
        output_image = output_image.resize(original_size, Image.LANCZOS)

        # Xuất log debug (đã xóa các dòng log thừa của ảnh xám)
        # Xuất log debug (đã xóa các dòng log thừa của ảnh xám)
        self._debug_image(image_sd,      "inpaint_input")
        self._debug_image(mask_raw,      "inpaint_mask_raw")
        self._debug_image(mask_sd,       "inpaint_mask_soft")
        self._debug_image(ref_sd,        "inpaint_reference")
        self._debug_image(raw_result,    "inpaint_raw")
        self._debug_image(output_image,  "inpaint_output")

        return await self.save_image(output_image)