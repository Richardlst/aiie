from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline,
    AutoencoderKL,
    ControlNetModel,
    DDIMScheduler,
)
import torch
import gc

from app.models import Img2ImgRequest, SDModel
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("Img2ImgService")
device = settings.DEVICE


class Img2ImgService(BaseSDService):
    def _get_pipe(self, model: SDModel) -> StableDiffusionControlNetImg2ImgPipeline:
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        vae = AutoencoderKL.from_pretrained(
            "stabilityai/sd-vae-ft-mse", torch_dtype=torch_dtype
        )

        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny", torch_dtype=torch_dtype
        )

        pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
            model.value,
            vae=vae,
            controlnet=controlnet,
            safety_checker=None,
            torch_dtype=torch_dtype,
        ).to(device)

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

        pipe = self._get_pipe(input.model)

        image = await self.process_image_url(input.image_url)

        image = self._resize_image(image)

        input = self._upgrade_prompt(input)

        canny_image = self._get_canny_map(
            image,
            input.canny_low_threshold,
            input.canny_high_threshold,
        )

        result = pipe(
            prompt=input.prompt,
            image=image,
            negative_prompt=input.negative_prompt,
            control_image=canny_image,
            controlnet_conditioning_scale=input.controlnet_conditioning_scale,
            num_inference_steps=input.num_inference_steps,
            guidance_scale=input.guidance_scale,
            strength=input.strength,
        )
        result = result.images[0]

        self._debug_image(image, "image")
        self._debug_image(canny_image, "canny_image")
        self._debug_image(result, "result")

        del pipe
        if device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

        return await self.save_image(result)
