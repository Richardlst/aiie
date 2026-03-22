from io import BytesIO
from fastapi import UploadFile
import numpy as np
import cv2
from PIL import Image
import torch
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
import requests

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
        self._init_face_detector()
        self._init_prompts()

    def _init_models(self):
        self.processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
        self.model = CLIPSegForImageSegmentation.from_pretrained(
            "CIDAS/clipseg-rd64-refined"
        )
        self.model.to(device)
        self.model.eval()

    def _init_face_detector(self):
        """Initialize OpenCV Haar cascade for face detection."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def _init_prompts(self):
        self.part_prompts = {
            "eyes": ["human eyes", "a pair of eyes", "open eyes"],
            "nose": ["human nose", "nose on face"],
            "lips": ["human lips", "mouth lips"],
            "face": ["human face", "face"],
            "head": ["human head", "head"],
            "hair": ["human hair", "hair"],
            "arm": ["human arm", "arm"],
            "leg": ["human leg", "leg"],
            "hand": ["human hand", "hand"],
            "foot": ["human foot", "foot"],
            "ear": ["human ear", "ear"],
            "neck": ["human neck", "neck"],
            "chest": ["human chest", "chest"],
            "body": ["human body", "body"],
            "back": ["human back", "back"],
            "waist": ["human waist", "waist"],
            "hips": ["human hips", "hips"],
            "thigh": ["human thigh", "thigh"],
            "knee": ["human knee", "knee"],
            "calf": ["human calf", "calf"],
        }

    def _get_region_bbox(self, image):
        """Detect face region using OpenCV Haar cascade."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        if len(faces) == 0:
            return None

        h, w = image.shape[:2]
        x, y, fw, fh = faces[0]
        padding = 0.1
        x_min = max(0, int(x - padding * fw))
        y_min = max(0, int(y - padding * fh))
        x_max = min(w, int(x + fw + padding * fw))
        y_max = min(h, int(y + fh + padding * fh))

        if x_max <= x_min or y_max <= y_min:
            return None

        return (x_min, y_min, x_max, y_max)

    def _process_image(self, image: np.ndarray, prompts: list) -> np.ndarray:
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        prompt = prompts[0] if isinstance(prompts, list) else prompts

        inputs = self.processor(images=pil_image, text=prompt, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        masks = torch.sigmoid(logits).detach().cpu().numpy()
        combined_mask = np.max(masks, axis=0)

        return combined_mask

    def _segment_region(self, image: np.ndarray, prompt: str):
        bbox = self._get_region_bbox(image)
        if bbox is None:
            mask = self._process_image(image, [prompt])
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
            return mask

        x_min, y_min, x_max, y_max = bbox
        region_image = image[y_min:y_max, x_min:x_max]
        region_mask = self._process_image(region_image, [prompt])

        full_mask = np.zeros((image.shape[0], image.shape[1]))
        region_mask_resized = cv2.resize(region_mask, (x_max - x_min, y_max - y_min))
        full_mask[y_min:y_max, x_min:x_max] = region_mask_resized

        return full_mask

    async def _load_image(self, image_url: str) -> np.ndarray:
        response = requests.get(image_url)
        image_data = response.content
        nparr = np.frombuffer(image_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    async def _save_result(self, result_image: Image.Image) -> str:
        # Chuyển đổi Image.Image thành BytesIO
        img_byte_arr = BytesIO()
        result_image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # Tạo UploadFile từ BytesIO
        upload_file = UploadFile(filename=get_unique_filename(), file=img_byte_arr)

        # Gọi phương thức upload_image
        response = await self.storage_service.upload_image(upload_file)

        # Log thông tin
        logger.info(f"Đã lưu ảnh thành công: {response.data.url}")
        logger.info(f"Kích thước ảnh: {result_image.size}")

        return response.data.url

    async def run(self, data: SegmentRequest) -> str:
        try:
            image = await self._load_image(data.image_url)
            prompt_list = [p.strip() for p in data.prompts.split(",")]

            combined_mask = np.zeros((image.shape[0], image.shape[1]))
            for prompt in prompt_list:
                mask = self._segment_region(image, prompt)
                combined_mask = np.maximum(combined_mask, mask)

            # Convert original BGR image to RGBA
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
            result[:, :, :3] = image_rgb
            # Alpha channel: 255 where mask > threshold, 0 (transparent) elsewhere
            result[:, :, 3] = (combined_mask > 0.08).astype(np.uint8) * 255
            result_pil = Image.fromarray(result, mode="RGBA")

            return await self._save_result(result_pil)

        except Exception as e:
            logger.error(f"Error in segmentation: {str(e)}")
            raise
