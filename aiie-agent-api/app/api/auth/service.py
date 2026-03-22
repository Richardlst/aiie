import uuid
from app.api.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    ResendEmailRequest,
    TokenData,
    ForgotPasswordRequest,
    VerifyEmailRequest,
    ResetPasswordRequest,
)
from app.api.user.models import User
from app.api.user.schemas import UserUpdate
from app.api.user.service import UserService
from app.api.mail.service import MailService
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
from app.core.settings import settings
from app.core.logger import setup_logger

logger = setup_logger("AuthService")


def _is_mail_configured() -> bool:
    """Check if mail credentials are properly configured (not placeholders)."""
    placeholder_values = {"your-email@gmail.com", "your-app-password", "", None}
    return (
        settings.MAIL_USERNAME not in placeholder_values
        and settings.MAIL_PASSWORD not in placeholder_values
    )


class AuthService:
    def __init__(self, user_service: UserService, mail_service: MailService = None):
        self.user_service = user_service
        self.mail_service = mail_service
        self.__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.__pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.__pwd_context.hash(password)

    def create_access_token(
        self,
        data: TokenData,
        expires_delta: timedelta = timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ),
    ) -> str:
        to_encode = data.model_dump()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        """Verify a token and return the token data if valid."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            # Explicit validation of expiration time
            current_time = datetime.now(timezone.utc).timestamp()
            if "exp" in payload and payload["exp"] < current_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token has expired",
                )

            token_data = TokenData(sub=payload.get("sub"), email=payload.get("email"))

            return token_data
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

    async def __authenticate_user(self, username: str, password: str) -> User:
        user = await self.user_service.get_by_email(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        if not self.__verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        return user

    async def register(self, user: RegisterRequest) -> RegisterResponse:
        existing_user = await self.user_service.get_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email has already been taken",
            )

        user.password = self.get_password_hash(user.password)
        new_user = await self.user_service.create(user)

        # Auto-activate user immediately (no email verification required)
        await self.user_service.update(id=new_user.id, user=UserUpdate(active=True))

        return new_user

    async def login(self, request: LoginRequest) -> LoginResponse:
        user = await self.__authenticate_user(request.username, request.password)

        token_data = TokenData(
            sub=str(user.id),
            email=user.email,
        )

        access_token = self.create_access_token(
            data=TokenData(**token_data.model_dump())
        )
        return LoginResponse(access_token=access_token)

    async def verify_email(self, request: VerifyEmailRequest):
        """Verify a user's email using the verification token."""
        # Verify the token
        token_data = self.verify_token(request.token)

        # Get the user
        user = await self.user_service.get_by_id(uuid.UUID(token_data.sub))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check if already verified
        if user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified"
            )

        # Activate the user
        await self.user_service.update(
            id=uuid.UUID(token_data.sub), user=UserUpdate(active=True)
        )

    async def resend_email(self, request: ResendEmailRequest):
        """Resend the verification email to a user."""
        # Check if user exists
        user = await self.user_service.get_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not _is_mail_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email service is not configured. Please contact the administrator.",
            )

        try:
            # Generate verification token
            token = self.create_access_token(
                data=TokenData(sub=str(user.id), email=user.email),
                expires_delta=timedelta(minutes=30),
            )

            # Send verification email
            await self.mail_service.send_verification_email(
                email_to=user.email,
                username=user.email.split("@")[0],
                token=token,
                base_url=settings.WEB_URI,
            )
        except Exception as e:
            logger.error(f"Failed to resend verification email: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to send verification email. Please try again later.",
            )

    async def forgot_password(self, request: ForgotPasswordRequest):
        """Send a password reset email to a user."""
        # Check if user exists
        user = await self.user_service.get_by_email(request.email)
        if not user:
            # Don't reveal that the email doesn't exist, just return success
            return None

        if not _is_mail_configured():
            logger.warning("Forgot password requested but mail is not configured.")
            return None

        try:
            # Generate password reset token
            token = self.create_access_token(
                data=TokenData(sub=str(user.id), email=user.email),
                expires_delta=timedelta(minutes=30),
            )

            # Send password reset email
            await self.mail_service.send_password_reset_email(
                email_to=user.email,
                username=user.email.split("@")[0],
                token=token,
                base_url=settings.WEB_URI,
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")

    async def reset_password(self, request: ResetPasswordRequest):
        """Reset a user's password using the reset token."""
        # Verify the token
        token_data = self.verify_token(request.token)

        # Get the user
        user = await self.user_service.get_by_id(uuid.UUID(token_data.sub))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Hash the new password
        hashed_password = self.get_password_hash(request.password)

        # Update the password
        await self.user_service.update(
            id=uuid.UUID(token_data.sub),
            user=UserUpdate(
                password=hashed_password,
            ),
        )
