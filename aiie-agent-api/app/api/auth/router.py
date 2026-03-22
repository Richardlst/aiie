from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth.dependencies import AuthServiceDep
from app.api.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    ForgotPasswordRequest,
    ResendEmailRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, auth_service: AuthServiceDep):
    return await auth_service.register(request)


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
):
    return await auth_service.login(
        LoginRequest(
            username=form_data.username,
            password=form_data.password,
        )
    )


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest, auth_service: AuthServiceDep):
    """Verify user's email address using token received via email."""
    await auth_service.verify_email(request)


@router.post("/resend-email")
async def resend_email(request: ResendEmailRequest, auth_service: AuthServiceDep):
    """Resend verification email to user."""
    await auth_service.resend_email(request)

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, auth_service: AuthServiceDep):
    """Send password reset email to user."""
    await auth_service.forgot_password(request)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, auth_service: AuthServiceDep):
    """Reset user password using token received via email."""
    await auth_service.reset_password(request)
