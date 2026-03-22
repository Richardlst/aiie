from diffusers import StableDiffusionPipeline
import torch
import gc

from app.models import SDModel, Text2ImgRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("Txt2ImgService")
device = settings.DEVICE


class Txt2ImgService(BaseSDService):
    def _get_pipe(self, model: SDModel) -> StableDiffusionPipeline:
        dtype = torch.float16 if device == "cuda" else torch.float32

        pipe = StableDiffusionPipeline.from_pretrained(
            model.value,
            torch_dtype=dtype,
            safety_checker=None,
        ).to(device)

        pipe.enable_attention_slicing(slice_size="auto")

        if device == "cuda" and dtype == torch.float16:
            try:
                pipe.enable_xformers_memory_efficient_attention()
                pipe.enable_model_cpu_offload()
                pipe.enable_vae_slicing()
                logger.info("Enabled xformers memory efficient attention")
            except Exception as e:
                logger.warning(f"Could not enable xformers: {e}")

        return pipe

    async def run(self, input: Text2ImgRequest) -> str:
        if device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        pipe = self._get_pipe(input.model)

        input = self._upgrade_prompt(input)

        result = pipe(
            prompt=input.prompt,
            negative_prompt=input.negative_prompt,
            num_inference_steps=input.num_inference_steps,
            guidance_scale=input.guidance_scale,
            width=input.width,
            height=input.height,
        ).images[0]

        self._debug_image(result, "result")

        del pipe
        if device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        return await self.save_image(result)
