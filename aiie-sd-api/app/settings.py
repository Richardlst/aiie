from pydantic_settings import BaseSettings
from pydantic import Field
import torch

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