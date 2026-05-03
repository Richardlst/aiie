from abc import ABC, abstractmethod
from io import BytesIO
import os
from PIL import Image
from fastapi import HTTPException, UploadFile
import cv2
import numpy as np

from app.models import BaseGenerationRequest
from app.service.storage import StorageService
from app.utils import get_unique_filename, process_image_url
from app.logger import setup_logger

logger = setup_logger("BaseService")


class BaseSDService(ABC):
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service

    @abstractmethod
    def run(self, input: BaseGenerationRequest) -> str:
        pass

    async def process_image_url(self, image_url: str) -> Image.Image:
        image = await process_image_url(image_url)
        if image is None:
            raise HTTPException(status_code=400, detail="Image is not valid")
        return image
    async def save_image(self, image: Image.Image) -> str:
        # Chuyển đổi Image.Image thành BytesIO
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Tạo UploadFile từ BytesIO - modified constructor
        filename = get_unique_filename()
        upload_file = UploadFile(
            filename=filename,
            file=img_byte_arr,
        )
        
        # Gọi phương thức upload_image
        response = await self.storage_service.upload_image(upload_file)
        
        # Log thông tin
        logger.info(f"Đã lưu ảnh thành công: {response.data.url}")
        logger.info(f"Kích thước ảnh: {image.size}")
        
        return response.data.url

    def _upgrade_prompt(self, request: BaseGenerationRequest) -> str:
        return request

    def _resize_image(
        self,
        image: Image.Image,
        max_dimension: int = 768,
    ) -> Image.Image:
        original_width, original_height = image.width, image.height

        bigger_side = max(original_width, original_height)
        scale = 1
        if bigger_side > max_dimension:
            scale = max_dimension / bigger_side
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            image = image.resize((new_width, new_height), Image.LANCZOS)
            logger.info(
                f"Resizing image from {original_width}x{original_height} to {new_width}x{new_height}"
            )
        return image

    def _get_canny_map(self, image, low_threshold=150, high_threshold=200):
        image_np = np.array(image)
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(image_gray, low_threshold, high_threshold)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(edges_colored)
    
    def _debug_image(self, image, filename):
        os.makedirs("debug", exist_ok=True)
        image.save(f"debug/{filename}.png")
