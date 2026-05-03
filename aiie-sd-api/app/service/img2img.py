import torch
import gc
import os
from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline,
    AutoencoderKL,
    ControlNetModel,
    DDIMScheduler,
)
from PIL import Image

from app.models import Img2ImgRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("Img2ImgService")
device = settings.DEVICE

class Img2ImgService(BaseSDService):
    def _get_pipe(self, lora_path: str = None) -> StableDiffusionControlNetImg2ImgPipeline:
        """
        Khởi tạo pipeline bằng cách load file checkpoint đơn lẻ (.safetensors).
        """
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        # 1. Load các thành phần bổ trợ từ folder pretrained (Hugging Face tự tải hoặc cache)
        vae = AutoencoderKL.from_pretrained(
            "stabilityai/sd-vae-ft-mse", 
            torch_dtype=torch_dtype
        )

        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny", 
            torch_dtype=torch_dtype
        )

        # 2. ĐƯỜNG DẪN FILE CHECKPOINT
        # Thêm r"" để Windows xử lý đúng dấu gạch chéo ngược \
        model_path = r"D:\aiie\aiie-sd-api\models\meinamix_v12Final.safetensors"

        # 3. SỬ DỤNG from_single_file thay vì from_pretrained
        # Lưu ý: Cần cài đặt 'pip install omegaconf' nếu chưa có
        pipe = StableDiffusionControlNetImg2ImgPipeline.from_single_file(
            model_path,
            vae=vae,
            controlnet=controlnet,
            torch_dtype=torch_dtype,
            safety_checker=None,
        ).to(device)

        # 4. Nạp LoRA Weights
        if lora_path and os.path.exists(lora_path):
            logger.info(f"Loading LoRA weights from {lora_path}")
            pipe.load_lora_weights(lora_path)
        else:
            logger.warning(f"LoRA path not found: {lora_path}")

        # 5. Tối ưu hóa VRAM 4GB
        if device == "cuda":
            pipe.enable_model_cpu_offload() 
            pipe.enable_vae_slicing()
            pipe.enable_attention_slicing()
            pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)

        return pipe

    async def run(self, input: Img2ImgRequest) -> str:
        if device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        # Đường dẫn tới file LoRA flat2
        lora_path = getattr(settings, "LORA_FLAT2_PATH", r"D:\aiie\aiie-sd-api\models\flat2.safetensors")
        pipe = self._get_pipe(lora_path=lora_path)

        image = await self.process_image_url(input.image_url)
        image = self._resize_image(image) 

        # Đảm bảo prompt có trigger word 'flat color'
        input = self._upgrade_prompt(input)

        canny_image = self._get_canny_map(
            image,
            input.canny_low_threshold,
            input.canny_high_threshold,
        )

        # Thực thi gen ảnh
        result = pipe(
            prompt=input.prompt,
            image=image,
            negative_prompt=input.negative_prompt,
            control_image=canny_image,
            controlnet_conditioning_scale=input.controlnet_conditioning_scale,
            num_inference_steps=input.num_inference_steps,
            guidance_scale=input.guidance_scale,
            strength=input.strength,
            cross_attention_kwargs={"scale": getattr(input, "lora_scale", 0.8)},
        )
        result = result.images[0]

        # Debug & Clear
        self._debug_image(image, "input")
        self._debug_image(result, "output")

        del pipe
        if device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        return await self.save_image(result)