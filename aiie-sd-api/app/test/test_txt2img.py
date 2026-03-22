from diffusers import StableDiffusionPipeline
import torch
import gc
import os
from datetime import datetime

# Import the Text2ImgRequest model and settings
from app.models import Text2ImgRequest, SDModel
from app.settings import settings

# Setup
device = settings.DEVICE
torch_dtype = torch.float16 if device == "cuda" else torch.float32

# Input from test_txt2img.py
input = Text2ImgRequest(
    prompt="A corgi dog lying comfortably on bright green lawn, white wooden farmhouse in background, afternoon sunlight, clear blue sky, detailed fur texture, relaxed posture, head resting on paws, warm golden hour lighting, photorealistic",
    # You can customize these parameters as needed
    model=SDModel.STABLE_DIFFUSION_V1_5,
    negative_prompt="deformed, blurry, bad anatomy, extra limbs, poorly drawn face, mutation, distorted, unrealistic background",
    num_inference_steps=30,
    guidance_scale=7.5,
    width=512,
    height=512,
)
num_images_per_prompt = 5  # Number of images to generate at once

# Clear CUDA cache if using GPU
if device == "cuda":
    torch.cuda.empty_cache()
    gc.collect()

# Load the pipeline
pipe = StableDiffusionPipeline.from_pretrained(
    input.model,
    torch_dtype=torch_dtype,
    safety_checker=None,
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

# Generate the images - now we're generating 2 images at once
results = pipe(
    prompt=input.prompt,
    negative_prompt=input.negative_prompt,
    num_inference_steps=input.num_inference_steps,
    guidance_scale=input.guidance_scale,
    width=input.width,
    height=input.height,
    num_images_per_prompt=num_images_per_prompt,  # Generate 2 images at once
).images

# Save the images to the debug directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
debug_dir = "eval/txt2img"
os.makedirs(debug_dir, exist_ok=True)
new_dir = os.path.join(debug_dir, timestamp)
if not os.path.exists(new_dir):
    os.makedirs(new_dir)  # Create a new directory for each timestamp
    
# Save each image with a unique ID
for i, image in enumerate(results):
    image_id = os.urandom(4).hex()
    filename = f"{image_id}.png"
    image_path = os.path.join(new_dir, filename)
    image.save(image_path)
    print(f"Image {i + 1} saved to {image_path}")

# Clean up resources
del pipe
if device == "cuda":
    torch.cuda.empty_cache()
    gc.collect()
