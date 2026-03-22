"""Email configuration for the application."""

from pydantic import BaseModel, EmailStr
from fastapi_mail import ConnectionConfig
from typing import List

from app.core.settings import settings


class EmailSchema(BaseModel):
    """Email schema for sending emails."""

    email: List[EmailStr]
    subject: str
    body: str = None
    template_name: str = None
    template_body: dict = None


# Configuration for FastAPI-Mail
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
    TEMPLATE_FOLDER="app/api/mail/templates",
)
