"""Dependency injection for mail services."""

from typing import Annotated

from fastapi import Depends
from app.api.mail.service import MailService


def get_mail_service() -> MailService:
    """Dependency for MailService."""
    return MailService()


MailServiceDep = Annotated[MailService, Depends(get_mail_service)]
