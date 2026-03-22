from pydantic import BaseModel, EmailStr

from app.api.user.models import UserBase
from app.api.user.schemas import UserResponse


class TokenData(BaseModel):
    sub: str  # user_id
    email: str


class RegisterRequest(UserBase):
    email: EmailStr
    password: str


class RegisterResponse(UserResponse):
    pass


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendEmailRequest(BaseModel):
    email: EmailStr
