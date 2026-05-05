from pydantic_settings import BaseSettings
from pydantic import Field
import torch
import os
import sys

# Configure HuggingFace Hub for better downloads on Windows
if sys.platform == "win32":
    os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "300"  # 5 minutes per chunk
    os.environ["HF_HUB_ETAG_TIMEOUT"] = "60"  # 1 minute for metadata
    os.environ["HF_HUB_CHUNK_TIMEOUT"] = "60"  # 1 minute per chunk
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_DATASETS_TRUST_REMOTE_CODE"] = "1"

device = "cuda" if torch.cuda.is_available() else "cpu"

class Settings(BaseSettings):
    DEFAULT_MODEL: str = Field(default="runwayml/stable-diffusion-v1-5")
    DEVICE: str = Field(default=device)
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_RETURN_ENDPOINT: str
    MINIO_SECURE: bool

    class Config:
        env_file = ".env"

settings = Settings()