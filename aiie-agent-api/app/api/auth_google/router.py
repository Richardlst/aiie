from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.api.auth_google.dependencies import GoogleAuthServiceDep
from app.api.auth_google.models import GoogleCallbackData
from app.core.settings import settings

router = APIRouter(prefix="/auth/google", tags=["auth_google"])


@router.get("/callback", response_model=GoogleCallbackData)
async def google_callback(
    google_auth_service: GoogleAuthServiceDep,
    code: str | None = None,
    error: str | None = None,
):
    if error == "access_denied":
        return RedirectResponse(f"{settings.WEB_URI}/auth/login")
        
    if not code:
        return RedirectResponse(f"{settings.WEB_URI}/auth/login")

    data = await google_auth_service.handle_callback(code)
    access_token = data.access_token

    redirect_url = f"{settings.WEB_URI}/auth/callback?access_token={access_token}&token_type=Bearer"

    return RedirectResponse(redirect_url)
