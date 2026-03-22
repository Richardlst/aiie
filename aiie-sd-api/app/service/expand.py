from diffusers import StableDiffusionInpaintPipeline, DDIMScheduler
from fastapi import HTTPException
import torch
from PIL import Image, ImageFilter
import numpy as np
import gc
import traceback
from typing import Optional

from app.models import ExpandRequest
from app.service.base_sd import BaseSDService
from app.settings import settings
from app.logger import setup_logger

logger = setup_logger("ExpandService")
device = settings.DEVICE

MODEL_ID = "runwayml/stable-diffusion-inpainting"

_pipe_cache: Optional[StableDiffusionInpaintPipeline] = None


def _load_pipe() -> StableDiffusionInpaintPipeline:
    global _pipe_cache
    if _pipe_cache is not None:
        return _pipe_cache

    logger.info(f"Loading expand pipeline ({MODEL_ID})...")
    torch_dtype = torch.float16 if device == "cuda" else torch.float32
    variant = "fp16" if device == "cuda" else None

    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch_dtype,
        safety_checker=None,
        variant=variant,
    )

    pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
    pipe.vae.enable_slicing()
    pipe.enable_attention_slicing(slice_size="auto")

    if device == "cuda":
        pipe.enable_model_cpu_offload()
        try:
            pipe.enable_xformers_memory_efficient_attention()
            logger.info("xformers enabled")
        except Exception as e:
            logger.warning(f"xformers not available: {e}")
    else:
        pipe.to("cpu")

    _pipe_cache = pipe
    logger.info("Expand pipeline ready.")
    return pipe


# â”€â”€ Tile-based outpainting constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Each SD call operates on a TILE_SIZE Ã— TILE_SIZE window so the model always
# works at its native resolution with full detail.
# CONTEXT  = how many pixels of already-good content to show as left/top context.
# STEP     = how many new pixels to generate per pass.
# By keeping CONTEXT = STEP = TILE_SIZE//2 we always provide equal context and
# generate equal new content, making every tile 50 % overlap.
TILE_SIZE = 512
CONTEXT   = 256
STEP      = 256


def _run_tile(
    pipe: StableDiffusionInpaintPipeline,
    tile: Image.Image,
    mask: Image.Image,
    prompt: str,
    negative_prompt: str,
    guidance_scale: float,
    num_steps: int,
    generator: torch.Generator,
) -> Image.Image:
    """Inpaint a single tile; resize to SD native res, return at original tile size."""
    orig_w, orig_h = tile.size
    # Scale so the longer side = TILE_SIZE, align to 8
    scale  = TILE_SIZE / max(orig_w, orig_h)
    sd_w   = max(8, int(orig_w * scale) // 8 * 8)
    sd_h   = max(8, int(orig_h * scale) // 8 * 8)
    t = tile.resize((sd_w, sd_h), Image.LANCZOS)
    m = mask.resize((sd_w, sd_h), Image.LANCZOS)
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=t,
        mask_image=m,
        guidance_scale=guidance_scale,
        num_inference_steps=num_steps,
        width=sd_w,
        height=sd_h,
        generator=generator,
    ).images[0]
    return result.resize((orig_w, orig_h), Image.LANCZOS)


def _expand_direction(
    canvas: Image.Image,
    direction: str,          # "right" | "left" | "bottom" | "top"
    expand_px: int,
    content_offset: int,     # where original content starts (expand_left / expand_top)
    pipe, prompt, negative_prompt, guidance_scale, num_steps, generator,
) -> Image.Image:
    """Expand canvas in one direction using overlapping 512-px tiles.

    Works on a mutable copy of `canvas` where the to-be-generated zone is
    already pre-filled (grey / edge-blur) but will be replaced tile by tile
    with coherent generated content.
    """
    cw, ch = canvas.size
    result = canvas.copy()
    remaining = expand_px
    pos = content_offset   # leading edge of already-generated content
    # For left/top expansion pos starts at content_offset and we go backward.
    # For right/bottom expansion pos starts at the content right/bottom edge.

    if direction == "right":
        content_edge = cw - expand_px    # right edge of original content
        pos = content_edge
        while remaining > 0:
            step    = min(STEP, remaining)
            context = min(CONTEXT, pos)
            x0, x1  = pos - context, pos + step
            tile = result.crop((x0, 0, x1, ch))
            mask = Image.new("L", (x1 - x0, ch), 0)
            mask.paste(255, (context, 0, x1 - x0, ch))
            mask = mask.filter(ImageFilter.GaussianBlur(radius=max(8, context // 4)))
            gen = _run_tile(pipe, tile, mask, prompt, negative_prompt, guidance_scale, num_steps, generator)
            result.paste(gen.crop((context, 0, x1 - x0, ch)), (pos, 0))
            pos += step; remaining -= step
            logger.info(f"Expand right: generated strip x={pos-step}..{pos}")

    elif direction == "left":
        content_edge = expand_px         # left edge of original content
        pos = content_edge
        while remaining > 0:
            step    = min(STEP, remaining)
            gen_end = pos
            gen_start = max(0, pos - step)
            context = min(CONTEXT, cw - gen_end)
            x0, x1 = gen_start, gen_end + context
            tile = result.crop((x0, 0, x1, ch))
            mask = Image.new("L", (x1 - x0, ch), 0)
            mask.paste(255, (0, 0, step, ch))
            mask = mask.filter(ImageFilter.GaussianBlur(radius=max(8, context // 4)))
            gen = _run_tile(pipe, tile, mask, prompt, negative_prompt, guidance_scale, num_steps, generator)
            result.paste(gen.crop((0, 0, step, ch)), (gen_start, 0))
            pos -= step; remaining -= step
            logger.info(f"Expand left: generated strip x={gen_start}..{gen_start+step}")

    elif direction == "bottom":
        content_edge = ch - expand_px
        pos = content_edge
        while remaining > 0:
            step    = min(STEP, remaining)
            context = min(CONTEXT, pos)
            y0, y1  = pos - context, pos + step
            tile = result.crop((0, y0, cw, y1))
            mask = Image.new("L", (cw, y1 - y0), 0)
            mask.paste(255, (0, context, cw, y1 - y0))
            mask = mask.filter(ImageFilter.GaussianBlur(radius=max(8, context // 4)))
            gen = _run_tile(pipe, tile, mask, prompt, negative_prompt, guidance_scale, num_steps, generator)
            result.paste(gen.crop((0, context, cw, y1 - y0)), (0, pos))
            pos += step; remaining -= step
            logger.info(f"Expand bottom: generated strip y={pos-step}..{pos}")

    elif direction == "top":
        content_edge = expand_px
        pos = content_edge
        while remaining > 0:
            step    = min(STEP, remaining)
            gen_end = pos
            gen_start = max(0, pos - step)
            context = min(CONTEXT, ch - gen_end)
            y0, y1 = gen_start, gen_end + context
            tile = result.crop((0, y0, cw, y1))
            mask = Image.new("L", (cw, y1 - y0), 0)
            mask.paste(255, (0, 0, cw, step))
            mask = mask.filter(ImageFilter.GaussianBlur(radius=max(8, context // 4)))
            gen = _run_tile(pipe, tile, mask, prompt, negative_prompt, guidance_scale, num_steps, generator)
            result.paste(gen.crop((0, 0, cw, step)), (0, gen_start))
            pos -= step; remaining -= step
            logger.info(f"Expand top: generated strip y={gen_start}..{gen_start+step}")

    return result


class ExpandService(BaseSDService):
    def _scale_to_fit(
        self, image: Image.Image, input: ExpandRequest, max_orig: int = 512
    ) -> Image.Image:
        """Scale original image down so it fits max_orig on the longer side.

        Expand offsets are scaled proportionally.  Keeping the original small
        means tiles stay at SD's native resolution without down-scaling.
        """
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
        logger.info(f"Scaled orig {w}x{h} â†’ {image.width}x{image.height}")
        return image

    async def run(self, input: ExpandRequest) -> str:
        try:
            if device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()

            image = await self.process_image_url(input.image_url)
            image = image.convert("RGB")
            # Keep original size — strips scale internally for SD

            el = max(0, input.expand_left)  // 8 * 8
            er = max(0, input.expand_right) // 8 * 8
            et = max(0, input.expand_top)   // 8 * 8
            eb = max(0, input.expand_bottom)// 8 * 8

            canvas_w = image.width  + el + er
            canvas_h = image.height + et + eb

            # Initial canvas: fill expansion zone with mean border colour.
            # Mean colour = no edges / no objects to confuse the model, just
            # approximate brightness/tone so the latent starting point is sane.
            arr     = np.array(image, dtype=np.float32)
            border  = np.concatenate([
                arr[0, :, :], arr[-1, :, :], arr[:, 0, :], arr[:, -1, :]
            ])
            mean_rgb = border.mean(axis=0).astype(np.uint8).tolist()
            canvas = Image.new("RGB", (canvas_w, canvas_h), tuple(mean_rgb))
            canvas.paste(image, (el, et))

            pipe  = _load_pipe()
            gen   = torch.Generator(device="cpu").manual_seed(42)
            prompt = input.prompt or "seamless natural continuation of the scene, same lighting, same style, high quality"
            neg    = input.negative_prompt or (
                "duplicate, mirror, seam, artifact, distorted, "
                "watermark, logo, signature, copyright, text, label, stamp, "
                "blurry, low quality"
            )
            guidance = input.guidance_scale
            steps    = input.num_inference_steps

            # ── Strip-based outpainting ────────────────────────────────────────
            # For each direction: take a narrow strip window (CONTEXT px of
            # existing content + STRIP_W px to generate) at 512px height/width.
            # The model sees mostly real content → generated strip matches scene.
            # Chain strips until the full expansion is filled.
            CONTEXT = 384   # px of real content shown to model each pass
            STRIP   = 128   # px generated per pass (max 128 for coherence)
            SD_SIZE = 512   # SD native resolution

            def _inpaint_strip(canvas: Image.Image, x0: int, y0: int,
                               w: int, h: int, gen_x: int, gen_y: int,
                               gen_w: int, gen_h: int) -> Image.Image:
                """
                Crop window (x0,y0,x0+w,y0+h), inpaint the gen region,
                paste back onto canvas, return updated canvas.
                gen_x/y are relative to the cropped window.
                """
                cw, ch = canvas.size
                x1, y1 = min(x0 + w, cw), min(y0 + h, ch)
                tile = canvas.crop((x0, y0, x1, y1))
                tw, th = tile.size
                # Clamp gen coordinates to actual tile size (crop may be smaller
                # than requested when the strip hits the canvas edge)
                actual_gen_x = min(gen_x, max(0, tw - 1))
                actual_gen_y = min(gen_y, max(0, th - 1))
                actual_gen_w = min(gen_w, tw - actual_gen_x)
                actual_gen_h = min(gen_h, th - actual_gen_y)
                if actual_gen_w <= 0 or actual_gen_h <= 0:
                    return canvas  # nothing to generate
                # Mask: white = generate, black = keep
                mask = Image.new("L", (tw, th), 0)
                mask.paste(255, (actual_gen_x, actual_gen_y,
                                 actual_gen_x + actual_gen_w,
                                 actual_gen_y + actual_gen_h))
                feather = max(8, STRIP // 4)
                mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))
                # Always resize to SD_SIZE x SD_SIZE square.
                # Even with aspect-ratio distortion the model still understands
                # the context and generates coherent content; distortion is
                # corrected when we resize the output back to (tw, th).
                t_s = tile.resize((SD_SIZE, SD_SIZE), Image.LANCZOS)
                m_s = mask.resize((SD_SIZE, SD_SIZE), Image.LANCZOS)
                out_s = pipe(
                    prompt=prompt, negative_prompt=neg,
                    image=t_s, mask_image=m_s,
                    guidance_scale=guidance,
                    num_inference_steps=steps,
                    width=SD_SIZE, height=SD_SIZE,
                    generator=gen,
                ).images[0]
                out = out_s.resize((tw, th), Image.LANCZOS)
                # Only paste the generated strip, preserve kept region exactly
                gen_region = out.crop((actual_gen_x, actual_gen_y,
                                       actual_gen_x + actual_gen_w,
                                       actual_gen_y + actual_gen_h))
                canvas.paste(gen_region, (x0 + actual_gen_x, y0 + actual_gen_y))
                return canvas

            def _slide_strips(canvas, direction, expand_px, content_start):
                """Slide strip window across expansion zone for one direction."""
                cw, ch = canvas.size
                remaining = expand_px
                if direction == "right":
                    pos = content_start   # right edge of filled content
                    while remaining > 0:
                        strip_w = min(STRIP, remaining)
                        ctx     = min(CONTEXT, pos)
                        x0      = pos - ctx
                        # Process full canvas height in ONE call — no y splits
                        canvas = _inpaint_strip(canvas, x0, 0, ctx + strip_w, ch,
                                                ctx, 0, strip_w, ch)
                        pos += strip_w; remaining -= strip_w
                elif direction == "left":
                    pos = content_start   # left edge of filled content
                    while remaining > 0:
                        strip_w = min(STRIP, remaining)
                        gen_start = pos - strip_w
                        ctx = min(CONTEXT, cw - pos)
                        x0 = gen_start
                        canvas = _inpaint_strip(canvas, x0, 0, strip_w + ctx, ch,
                                                0, 0, strip_w, ch)
                        pos -= strip_w; remaining -= strip_w
                elif direction == "bottom":
                    pos = content_start
                    while remaining > 0:
                        strip_h = min(STRIP, remaining)
                        ctx     = min(CONTEXT, pos)
                        y0      = pos - ctx
                        # Process full canvas width in ONE call — no x splits
                        canvas = _inpaint_strip(canvas, 0, y0, cw, ctx + strip_h,
                                                0, ctx, cw, strip_h)
                        pos += strip_h; remaining -= strip_h
                elif direction == "top":
                    pos = content_start
                    while remaining > 0:
                        strip_h = min(STRIP, remaining)
                        gen_start = pos - strip_h
                        ctx = min(CONTEXT, ch - pos)
                        y0 = gen_start
                        canvas = _inpaint_strip(canvas, 0, y0, cw, strip_h + ctx,
                                                0, 0, cw, strip_h)
                        pos -= strip_h; remaining -= strip_h
                return canvas

            # Expand right/left before top/bottom so corners are filled
            if er > 0:
                canvas = _slide_strips(canvas, "right",  er, el + image.width)
            if el > 0:
                canvas = _slide_strips(canvas, "left",   el, el)
            if eb > 0:
                canvas = _slide_strips(canvas, "bottom", eb, et + image.height)
            if et > 0:
                canvas = _slide_strips(canvas, "top",    et, et)

            # Guarantee original pixels are untouched
            canvas.paste(image, (el, et))

            self._debug_image(canvas, "expand_result")
            return await self.save_image(canvas)

        except HTTPException:
            raise
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"Expand error: {e}\n{tb}")
            import os
            os.makedirs("debug", exist_ok=True)
            with open("debug/expand_error.txt", "w") as f:
                f.write(tb)
            raise HTTPException(status_code=500, detail=f"Expand failed: {str(e)}")

            # ── Step 1: Reflect-pad the canvas ────────────────────────────────
            # np.pad 'reflect' mirrors the image content outward.
            # This gives the expanded zones colour, texture and structure that
            # naturally matches the original scene — trees remain trees, sky
            # remains sky, etc.
            # If the expansion is larger than the image, we clamp to image size
            # (numpy reflect cannot pad more than dim-1 pixels per side).
            arr = np.array(image, dtype=np.uint8)
            pad_t = min(et, image.height - 1)
            pad_b = min(eb, image.height - 1)
            pad_l = min(el, image.width  - 1)
            pad_r = min(er, image.width  - 1)
            reflected = np.pad(arr, ((pad_t, pad_b), (pad_l, pad_r), (0, 0)), mode="reflect")

            # If expansion exceeds image size, edge-pad the remaining pixels
            pt2 = et - pad_t; pb2 = eb - pad_b
            pl2 = el - pad_l; pr2 = er - pad_r
            if pt2 or pb2 or pl2 or pr2:
                reflected = np.pad(reflected, ((pt2, pb2), (pl2, pr2), (0, 0)), mode="edge")

            canvas = Image.fromarray(reflected[:canvas_h, :canvas_w])

            # ── Step 2: Smooth the reflection seam with SD ────────────────────
            # Mask only a narrow band around the seam between original and reflected
            # content.  Low strength (0.35) means SD barely denoises — enough to
            # remove the hard mirror-line but not enough to hallucinate new objects.
            seam = max(24, min(el, er, et, eb, 48) if (el and er and et and eb) else 32)
            mask = Image.new("L", (canvas_w, canvas_h), 0)   # black = keep
            # Paint white seam band around the original image border
            if el > 0:
                mask.paste(255, (el, 0, el + seam, canvas_h))
            if er > 0:
                mask.paste(255, (canvas_w - er - seam, 0, canvas_w - er, canvas_h))
            if et > 0:
                mask.paste(255, (0, et, canvas_w, et + seam))
            if eb > 0:
                mask.paste(255, (0, canvas_h - eb - seam, canvas_w, canvas_h - eb))
            mask = mask.filter(ImageFilter.GaussianBlur(radius=seam // 2))

            pipe = _load_pipe()
            gen  = torch.Generator(device="cpu").manual_seed(42)

            # Resize canvas to SD-native resolution for inference
            scale_sd = min(1.0, 768 / max(canvas_w, canvas_h))
            sd_w = max(8, int(canvas_w * scale_sd) // 8 * 8)
            sd_h = max(8, int(canvas_h * scale_sd) // 8 * 8)
            canvas_sd = canvas.resize((sd_w, sd_h), Image.LANCZOS)
            mask_sd   = mask.resize((sd_w, sd_h),   Image.LANCZOS)

            result_sd = pipe(
                prompt=input.prompt or "seamless natural scene, same lighting, same style",
                negative_prompt=input.negative_prompt or (
                    "seam, border, line, artifact, blurry, distorted, watermark"
                ),
                image=canvas_sd,
                mask_image=mask_sd,
                strength=0.35,          # low — just smooth the seam, don't regenerate
                guidance_scale=input.guidance_scale,
                num_inference_steps=input.num_inference_steps,
                width=sd_w,
                height=sd_h,
                generator=gen,
            ).images[0]

            result = result_sd.resize((canvas_w, canvas_h), Image.LANCZOS)

            # Guarantee original pixels are pixel-perfect
            result.paste(image, (el, et))

            self._debug_image(canvas, "expand_reflected")
            self._debug_image(result, "expand_result")
            return await self.save_image(result)

        except HTTPException:
            raise
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"Expand error: {e}\n{tb}")
            import os
            os.makedirs("debug", exist_ok=True)
            with open("debug/expand_error.txt", "w") as f:
                f.write(tb)
            raise HTTPException(status_code=500, detail=f"Expand failed: {str(e)}")

