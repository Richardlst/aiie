from io import BytesIO
from PIL import Image
import os
import uuid
from datetime import datetime
import aiohttp
from fastapi import HTTPException

from app.logger import setup_logger
from app.models import UploadResponse
from app.settings import settings

logger = setup_logger("Utils")


async def process_image_url(image_url: str) -> Image.Image:
    """Tải và xử lý ảnh từ URL"""
    if not image_url:
        logger.error("URL ảnh không được để trống")
        raise HTTPException(status_code=400, detail="URL ảnh không được để trống")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status != 200:
                    error_msg = (
                        f"Không thể tải ảnh từ URL. Status code: {response.status}"
                    )
                    logger.error(error_msg)
                    raise HTTPException(status_code=400, detail=error_msg)

                image_data = await response.read()
                if not image_data:
                    raise ValueError("Dữ liệu ảnh trống")

                image = Image.open(BytesIO(image_data))
                if not image:
                    raise ValueError("Không thể mở ảnh")

                # Đảm bảo ảnh là RGB
                if image.mode == "RGBA":
                    # Tạo background trắng
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    # Paste ảnh RGBA lên background trắng
                    background.paste(image, mask=image.split()[3])
                    image = background
                elif image.mode != "RGB":
                    image = image.convert("RGB")

                logger.info(
                    f"Đã xử lý ảnh thành công, mode: {image.mode}, size: {image.size}"
                )
                return image

    except HTTPException:
        raise
    except ValueError as ve:
        error_msg = f"Lỗi khi xử lý ảnh: {str(ve)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Lỗi không xác định khi xử lý ảnh: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


def get_unique_filename(original_filename: str = None) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]

    if original_filename:
        ext = os.path.splitext(original_filename)[1]
    else:
        ext = ".png"

    return f"{timestamp}_{unique_id}{ext}"


async def save_image(image: Image.Image, filename: str) -> str:
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    form = aiohttp.FormData()
    form.add_field("file", img_byte_arr, filename=filename, content_type="image/png")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.AGENT_API_URL}/upload", data=form
        ) as response:
            if response.status != 200:
                print(response)
                error_msg = f"Lỗi khi upload ảnh. Status code: {response.status}"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)

            result = await response.json()
            result = UploadResponse(**result)
            return result.data.url
