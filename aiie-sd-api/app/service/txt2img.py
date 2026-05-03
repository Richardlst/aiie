import gc
import torch
import traceback # 🟢 Thêm thư viện này để in lỗi chi tiết
from typing import Optional
from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler

from app.models import Text2ImgRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("Txt2ImgService")
device = settings.DEVICE

MODEL_PATH = "./models/realisticVisionV60B1_v51HyperVAE.safetensors"

_pipe_cache: Optional[StableDiffusionPipeline] = None

class Txt2ImgService(BaseSDService):
    def _get_pipe(self) -> StableDiffusionPipeline:
        global _pipe_cache
        if _pipe_cache is not None:
            return _pipe_cache

        dtype = torch.float16 if device == "cuda" else torch.float32
        logger.info(f"Loading Standard Txt2Img model: {MODEL_PATH}")
        
        pipe = StableDiffusionPipeline.from_single_file(
            MODEL_PATH,
            torch_dtype=dtype,
            safety_checker=None,
        )

        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
        
        if device == "cuda":
            pipe.to(device)
            pipe.enable_attention_slicing(slice_size="auto")
            pipe.enable_vae_slicing()
            try:
                pipe.enable_xformers_memory_efficient_attention()
            except Exception as e:
                pass
        
        _pipe_cache = pipe
        return pipe

    async def run(self, input: Text2ImgRequest) -> str:
        try: # 🟢 BẮT ĐẦU ÉP CUNG
            if device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()

            pipe = self._get_pipe()
            input = self._upgrade_prompt(input)

            actual_steps = 6 if input.num_inference_steps > 10 else input.num_inference_steps
            actual_cfg = 1.5 if input.guidance_scale > 3.0 else input.guidance_scale
            
            w = input.width or 512
            h = input.height or 512

            logger.info(f"Generating Txt2Img: steps={actual_steps}, cfg={actual_cfg}")

            generator = torch.Generator(device=device).manual_seed(42)

            result = pipe(
                prompt=input.prompt,
                negative_prompt=input.negative_prompt,
                num_inference_steps=actual_steps,
                guidance_scale=actual_cfg,
                width=w,
                height=h,
                generator=generator,
            ).images[0]

            self._debug_image(result, "txt2img_result")
            return await self.save_image(result)
            
        except Exception as e:
            # 🟢 IN LỖI RA MÀN HÌNH TERMINAL 8001
            print("\n" + "🔥"*20)
            print("LỖI CHÍNH MẠNG TẠI SD API (8001):")
            traceback.print_exc()
            print("🔥"*20 + "\n")
            raise # Ném lại lỗi 500 cho Agent