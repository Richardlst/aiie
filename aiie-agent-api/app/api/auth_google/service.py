import uuid
import httpx
from urllib.parse import urlencode
from fastapi import HTTPException, Request, status


from app.api.auth.schemas import TokenData
from app.api.auth.service import AuthService
from app.api.auth_google.models import GoogleCallbackData, GoogleUserProfile
from app.api.user.models import User
from app.api.user.schemas import UserCreate
from app.api.user.service import UserService
from app.core.settings import settings
from app.core.logger import setup_logger

logger = setup_logger("GoogleAuthService")


class GoogleAuthService:
    def __init__(self, user_service: UserService, auth_service: AuthService):
        self._user_service = user_service
        self._auth_service = auth_service

    async def _fetch_access_token(self, code: str) -> dict:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
            "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.OAUTH_GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
        if response.status_code != 200:
            logger.exception(f"Google authentication failed: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google authentication failed: {response.text}",
            )
        return response.json()

    async def _fetch_user_profile(self, access_token: str) -> GoogleUserProfile:
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to retrieve Google user profile: {response.text}",
            )
        return GoogleUserProfile(**response.json())

    async def _create_or_get_user(self, user_profile: GoogleUserProfile) -> User:
        user = await self._user_service.get_by_email(user_profile.email)
        if not user:
            user = await self._user_service.create(
                UserCreate(
                    email=user_profile.email,
                    password=str(uuid.uuid4()),
                    active=True,
                )
            )
        return user

    async def handle_callback(self, code: str) -> GoogleCallbackData:
        access_token_data = await self._fetch_access_token(code)
        access_token = access_token_data.get("access_token")

        user_profile = await self._fetch_user_profile(access_token)
        user = await self._create_or_get_user(user_profile)

        token_data = TokenData(
            sub=str(user.id),
            email=user.email,
        )
        access_token = self._auth_service.create_access_token(data=token_data)

        return GoogleCallbackData(access_token=access_token)
