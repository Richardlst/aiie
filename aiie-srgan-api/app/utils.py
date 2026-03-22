import os
from fastapi import HTTPException
from app.logger import setup_logger
import numpy as np
import tensorlayerx as tlx
from .srgan import SRGAN_g
import cv2
import requests
from io import BytesIO
from PIL import Image
from app.settings import settings
import uuid
from minio import Minio
import json

logger = setup_logger("Utils")

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)

# Create bucket if not exists
if not minio_client.bucket_exists("images"):
    minio_client.make_bucket("images")
    # Set policy cho bucket là public-read
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::images/*"],
            }
        ],
    }
    minio_client.set_bucket_policy("images", json.dumps(policy))

os.environ["TL_BACKEND"] = "tensorflow"

tlx.set_device("GPU")

G = SRGAN_g()
G.init_build(tlx.nn.Input(shape=(1, 96, 96, 3)))

G.load_weights(os.path.join("models/g.npz"), format="npz_dict")
G.set_eval()


async def upscale_image(url):
    try:
        logger.info(f"Starting upscale for URL: {url}")
        lr_img = download_image(url)
        logger.info(f"Input image shape: {lr_img.shape}")

        sr_img = process_batch_image(G, lr_img, patch_size=256, overlap=32)
        logger.info(f"Output image shape: {sr_img.shape}")
    except Exception as e:
        logger.error(f"Error in upscale_image: {str(e)}", exc_info=True)
        raise

    sr_img_bgr = cv2.cvtColor(sr_img, cv2.COLOR_RGB2BGR)

    # Chuyển BGR sang RGB và tạo PIL Image
    sr_img_rgb = cv2.cvtColor(sr_img_bgr, cv2.COLOR_BGR2RGB)
    output_image = Image.fromarray(sr_img_rgb)

    # Lưu ảnh và lấy URL
    output_url = await upload_image(output_image, "processed_image.png")
    logger.info(f"Uploaded image URL: {output_url}")

    # Cleanup
    import gc
    gc.collect()

    # Return response in correct format
    logger.info(f"Returning URL: {output_url}")
    return output_url


def process_image(G, lr_img):
    valid_lr_img_tensor = lr_img / 127.5 - 1

    # Thay đổi cách chuẩn bị tensor cho format NHWC
    valid_lr_img_tensor = np.asarray(valid_lr_img_tensor, dtype=np.float32)
    # Không cần transpose nữa vì đã ở format NHWC
    valid_lr_img_tensor = valid_lr_img_tensor[np.newaxis, :, :, :]
    valid_lr_img_tensor = tlx.ops.convert_to_tensor(valid_lr_img_tensor)

    out = tlx.ops.convert_to_numpy(G(valid_lr_img_tensor))
    out = np.asarray((out + 1) * 127.5, dtype=np.uint8)
    # Không cần transpose nữa vì output đã ở format HWC
    out = out[0]

    return out


def process_batch_image(G, lr_img, patch_size=512, overlap=32):
    h, w = lr_img.shape[:2]

    n_h = (h + patch_size - 1) // patch_size
    n_w = (w + patch_size - 1) // patch_size

    print(f"Splitting image {(h, w)} into {n_h}x{n_w} patches")

    scale = 4
    output = np.zeros((h * scale, w * scale, 3), dtype=np.float32)
    weight = np.zeros_like(output)

    for i in range(n_h):
        for j in range(n_w):
            logger.info(f"Processing patch ({i}, {j})...")
            top = i * patch_size
            left = j * patch_size
            bottom = min(top + patch_size + overlap, h)
            right = min(left + patch_size + overlap, w)

            patch = lr_img[top:bottom, left:right]
            logger.info(f"Patch size: {patch.shape}")

            # Thay đổi cách chuẩn bị tensor cho format NHWC
            patch_tensor = (patch / 127.5) - 1
            # Chỉ thêm batch dimension, không chuyển CHW
            patch_tensor = patch_tensor[np.newaxis, ...]
            patch_tensor = tlx.ops.convert_to_tensor(patch_tensor.astype(np.float32))

            try:
                logger.info(f"Running model on patch ({i}, {j})...")
                sr_patch = G(patch_tensor)
                sr_patch = tlx.ops.convert_to_numpy(sr_patch)

                # Chuyển về khoảng [0, 1]
                sr_patch = (sr_patch + 1) / 2
                # Bỏ batch dimension, không cần transpose nữa vì đã ở format HWC
                sr_patch = sr_patch[0]

                top_sr = top * scale
                left_sr = left * scale
                bottom_sr = bottom * scale
                right_sr = right * scale

                mask = np.ones_like(sr_patch)
                if overlap > 0:
                    mask = create_blending_mask(sr_patch.shape[:2])

                output[top_sr:bottom_sr, left_sr:right_sr] += sr_patch * mask
                weight[top_sr:bottom_sr, left_sr:right_sr] += mask

                print(f"Processed patch ({i}, {j})")

            except Exception as e:
                print(f"Error processing patch ({i}, {j}): {str(e)}")
                continue

    output = np.divide(output, weight, where=weight != 0)
    output = np.clip(output * 255, 0, 255).astype(np.uint8)

    return output


def create_blending_mask(shape):
    """Tạo mask để blend các patches"""
    h, w = shape
    mask = np.ones((h, w), dtype=np.float32)

    # Tạo gradient ở các cạnh
    gradient_size = 32
    for i in range(gradient_size):
        alpha = i / gradient_size
        mask[i, :] *= alpha
        mask[-i - 1, :] *= alpha
        mask[:, i] *= alpha
        mask[:, -i - 1] *= alpha

    return mask[..., np.newaxis]


def download_image(url):
    response = requests.get(url)
    if not response.headers["content-type"].startswith("image/"):
        raise ValueError("URL provided is not an image")

    pil_image = Image.open(BytesIO(response.content))

    # Chuyển đổi RGBA sang RGB nếu cần
    if pil_image.mode == "RGBA":
        pil_image = pil_image.convert("RGB")

    # Chuyển PIL Image thành numpy array
    valid_img = np.asarray(pil_image)
    return valid_img


async def upload_image(image: Image.Image, filename: str) -> str:
    try:
        # Tạo unique filename
        file_extension = filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Convert PIL Image to bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        file_data = img_byte_arr.getvalue()

        # Upload file
        minio_client.put_object(
            "images",
            unique_filename,
            data=BytesIO(file_data),
            length=len(file_data),
            content_type="image/png",
        )

        # Trả về direct URL
        endpoint = settings.MINIO_RETURN_ENDPOINT
        if settings.MINIO_SECURE:
            url = f"https://{endpoint}/images/{unique_filename}"
        else:
            url = f"http://{endpoint}/images/{unique_filename}"
            
        return url
    except Exception as e:
        error_msg = f"Lỗi khi upload ảnh: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
