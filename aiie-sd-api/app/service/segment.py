from io import BytesIO
from fastapi import UploadFile
import numpy as np
import cv2
from PIL import Image
import torch
import requests
import os

from transformers import GroundingDinoForObjectDetection, GroundingDinoProcessor
from segment_anything import sam_model_registry, SamPredictor

from app.service.storage import StorageService
from app.settings import settings
from app.models import SegmentRequest
from app.logger import setup_logger
from app.utils import get_unique_filename

logger = setup_logger("SegmentationService")
device = settings.DEVICE

class SegmentationService:
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
        self._init_models()

    def _init_models(self):
        logger.info("Đang khởi tạo Pipeline Grounded-SAM (Manual Edition)...")
        try:
            # 1. Khởi tạo GroundingDINO Tiny (Text-to-Box)
            repo_id = "IDEA-Research/grounding-dino-tiny"
            self.gdino_processor = GroundingDinoProcessor.from_pretrained(repo_id)
            self.gdino_model = GroundingDinoForObjectDetection.from_pretrained(repo_id).to(device)
            
            # 2. Khởi tạo SAM (Box-to-Mask)
            # Tải file sam_vit_b_01ec64.pth về thư mục gốc nếu chưa có
            sam_type = "vit_b" 
            checkpoint_path = "models/sam_vit_b_01ec64.pth"
            
            if not os.path.exists(checkpoint_path):
                logger.warning(f"CẢNH BÁO: Không tìm thấy file {checkpoint_path}. Model SAM sẽ chạy không chính xác.")
                self.sam = sam_model_registry[sam_type](checkpoint=None)
            else:
                self.sam = sam_model_registry[sam_type](checkpoint=checkpoint_path)
                
            self.sam.to(device)
            self.sam_predictor = SamPredictor(self.sam)
            
            logger.info("Khởi tạo Pipeline thành công!")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo model: {str(e)}")
            raise

    async def _load_image(self, image_url: str) -> np.ndarray:
        response = requests.get(image_url)
        nparr = np.frombuffer(response.content, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def _get_boxes(self, image_pil, prompt):
        # Đảm bảo prompt kết thúc bằng dấu chấm
        p = prompt.strip()
        if not p.endswith("."):
            p += "."
            
        inputs = self.gdino_processor(images=image_pil, text=p, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = self.gdino_model(**inputs)
        
        # Hạ ngưỡng threshold xuống 0.2 để nhạy hơn, tránh việc không tìm thấy box (gây trắng ảnh)
        results = self.gdino_processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=0.2, 
            text_threshold=0.2,
            target_sizes=[image_pil.size[::-1]]
        )[0]
        
        return results["boxes"]

    def _process_image(self, image_np, prompt: str) -> np.ndarray:
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        
        # 1. Lấy boxes từ GroundingDINO
        boxes = self._get_boxes(image_pil, prompt)
        logger.info(f"Prompt: '{prompt}' - Tìm thấy {len(boxes)} đối tượng.")
        
        if len(boxes) == 0:
            return np.zeros((image_np.shape[0], image_np.shape[1]), dtype=bool)

        # 2. Dùng SAM để cắt mask
        self.sam_predictor.set_image(image_rgb)
        
        # Áp dụng dự đoán mask cho tất cả các box tìm thấy
        transformed_boxes = self.sam_predictor.transform.apply_boxes_torch(boxes, image_np.shape[:2])
        
        with torch.no_grad():
            masks, _, _ = self.sam_predictor.predict_torch(
                point_coords=None,
                point_labels=None,
                boxes=transformed_boxes,
                multimask_output=False,
            )
        
        # LOGIC QUAN TRỌNG: Gộp tất cả mask lại thành một mảng 2D duy nhất
        # masks có shape [N, 1, H, W], cần gộp N và xóa chiều 1
        combined_mask = torch.any(masks.squeeze(1), dim=0).cpu().numpy()
        return combined_mask

    async def _save_result(self, result_image: Image.Image) -> str:
        img_byte_arr = BytesIO()
        result_image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        
        upload_file = UploadFile(filename=get_unique_filename(), file=img_byte_arr)
        response = await self.storage_service.upload_image(upload_file)
        return response.data.url

    async def run(self, data: SegmentRequest) -> str:
        try:
            image_cv2 = await self._load_image(data.image_url)
            h, w = image_cv2.shape[:2]
            
            prompt_list = [p.strip() for p in data.prompts.split(",") if p.strip()]
            final_mask = np.zeros((h, w), dtype=bool)

            for prompt in prompt_list:
                mask = self._process_image(image_cv2, prompt)
                # Gộp mask của các prompt khác nhau bằng phép OR
                final_mask = np.logical_or(final_mask, mask)

            # Tạo kết quả RGBA (Trong suốt vùng không có mask)
            result = np.zeros((h, w, 4), dtype=np.uint8)
            result[:, :, :3] = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
            result[:, :, 3] = final_mask.astype(np.uint8) * 255

            return await self._save_result(Image.fromarray(result, mode="RGBA"))
            
        except Exception as e:
            logger.error(f"Segmentation Error: {str(e)}")
            raise