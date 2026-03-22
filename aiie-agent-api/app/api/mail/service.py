"""Email service for sending emails."""

from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from typing import List, Dict, Any

from app.api.mail.config import mail_config


class MailService:
    """Service for sending emails."""

    def __init__(self):
        self.mail_config = mail_config
        self.fast_mail = FastMail(self.mail_config)

    async def send_email(
        self,
        email_to: List[EmailStr],
        subject: str,
        body: str = None,
        template_name: str = None,
        template_body: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        """
        Send an email to the specified recipients.

        Args:
            email_to: List of recipient email addresses
            subject: Email subject
            body: Plain text email body (used if no template)
            template_name: Name of the email template to use
            template_body: Variables to pass to the email template

        Returns:
            A dictionary containing the message status
        """
        # Setup the email message
        message = MessageSchema(
            subject=subject,
            recipients=[str(email) for email in email_to],
            template_body=template_body,
            body=body,
            subtype=MessageType.html,
        )

        # Send the email with or without a template
        if template_name:
            await self.fast_mail.send_message(message, template_name=template_name)
        else:
            await self.fast_mail.send_message(message)

        return {"status": "success", "message": "Email sent successfully"}

    async def send_verification_email(
        self, email_to: EmailStr, username: str, token: str, base_url: str
    ) -> Dict[str, str]:
        """
        Send a verification email to a new user.

        Args:
            email_to: Recipient email address
            username: Username of the recipient
            token: Verification token
            base_url: Base URL for the verification link

        Returns:
            A dictionary containing the message status
        """
        # Create verification URL
        verification_url = f"{base_url}/auth/verify-email?token={token}"

        # Email template variables
        template_body = {
            "username": username,
            "verification_url": verification_url,
        }

        return await self.send_email(
            email_to=[email_to],
            subject="Verify your email address",
            template_name="verification.html",
            template_body=template_body,
        )

    async def send_password_reset_email(
        self, email_to: EmailStr, username: str, token: str, base_url: str
    ) -> Dict[str, str]:
        """
        Send a password reset email to a user.

        Args:
            email_to: Recipient email address
            username: Username of the recipient
            token: Reset token
            base_url: Base URL for the reset link

        Returns:
            A dictionary containing the message status
        """
        # Create reset URL
        reset_url = f"{base_url}/auth/reset-password?token={token}"

        # Email template variables
        template_body = {
            "username": username,
            "reset_url": reset_url,
        }

        return await self.send_email(
            email_to=[email_to],
            subject="Reset your password",
            template_name="password_reset.html",
            template_body=template_body,
        )
