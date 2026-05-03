from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline,
    ControlNetModel,
    AutoencoderKL,
)
import torch
import gc
import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
import glob
from tqdm import tqdm

# Import the Img2ImgRequest model and settings
from app.models import Img2ImgRequest
from app.settings import settings

# Setup
device = settings.DEVICE
torch_dtype = torch.float16 if device == "cuda" else torch.float32

# Configuration parameters
input_dir = "input_images"  # Path to directory containing input images
output_dir = "eval/img2img"  # Directory to save transformed images

# Create Img2ImgRequest object with parameters
input = Img2ImgRequest(
    image_url="dummy_url",  # This will be replaced in the process function
    prompt="A magical fairy-tale castle on a floating island, ethereal lighting, vibrant colors, fantasy landscape, detailed architecture, dreamy atmosphere, 8k, hyper-detailed, professional digital art",
    negative_prompt="deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated, ugly, poorly drawn, low quality, grainy",
    num_inference_steps=40,
    guidance_scale=9.0,
    strength=0.75,
    canny_low_threshold=100,
    canny_high_threshold=200,
    controlnet_conditioning_scale=0.6,
)


def process_image(image_path, output_path, pipe, input_config):
    """Process a single image with the img2img pipeline"""
    try:
        # Load source image
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Create canny edge map
        image_np = np.array(image)
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(
            image_gray,
            input_config.canny_low_threshold,
            input_config.canny_high_threshold,
        )
        canny_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        canny_image = Image.fromarray(canny_image)

        # Generate the transformed image
        result = pipe(
            prompt=input_config.prompt,
            image=image,
            negative_prompt=input_config.negative_prompt,
            control_image=canny_image,
            controlnet_conditioning_scale=input_config.controlnet_conditioning_scale,
            num_inference_steps=input_config.num_inference_steps,
            guidance_scale=input_config.guidance_scale,
            strength=input_config.strength,
        ).images[0]

        # Save the result
        result.save(output_path)
        return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False


# Clear CUDA cache if using GPU
if device == "cuda":
    torch.cuda.empty_cache()
    gc.collect()

# Create output directory with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
new_dir = os.path.join(output_dir, timestamp)
os.makedirs(new_dir, exist_ok=True)

print(f"Processing images from {input_dir}")
print(f"Saving results to {new_dir}")
print(f"Using prompt: {input.prompt}")

# Load the pipeline components
print("Loading model components...")

vae = AutoencoderKL.from_pretrained(
    "stabilityai/sd-vae-ft-mse", torch_dtype=torch_dtype
)

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny", torch_dtype=torch_dtype
)

# Create the pipeline
pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    vae=vae,
    controlnet=controlnet,
    safety_checker=None,
    torch_dtype=torch_dtype,
).to(device)

# Enable optimizations
pipe.enable_attention_slicing(slice_size="auto")

if device == "cuda" and torch_dtype == torch.float16:
    try:
        pipe.enable_xformers_memory_efficient_attention()
        pipe.enable_model_cpu_offload()
        pipe.enable_vae_slicing()
        print("Enabled xformers memory efficient attention")
    except Exception as e:
        print(f"Could not enable xformers: {e}")

# Get list of image files in input directory
image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]
image_files = []
for ext in image_extensions:
    image_files.extend(glob.glob(os.path.join(input_dir, ext)))

if not image_files:
    print(f"No image files found in {input_dir}")
else:
    print(f"Found {len(image_files)} image files")

    # Process each image
    successful = 0
    failed = 0

    for img_path in tqdm(image_files, desc="Processing images"):
        # Create output path with same filename in output directory
        filename = os.path.basename(img_path)
        base_name, ext = os.path.splitext(filename)
        output_path = os.path.join(new_dir, f"{base_name}.png")

        # Process the image
        success = process_image(img_path, output_path, pipe, input)

        if success:
            successful += 1
        else:
            failed += 1

    print(
        f"Processing complete! Successfully processed: {successful}, Failed: {failed}"
    )

# Clean up resources
del pipe
if device == "cuda":
    torch.cuda.empty_cache()
    gc.collect()
