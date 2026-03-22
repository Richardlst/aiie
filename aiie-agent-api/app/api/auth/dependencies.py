from typing import Annotated, Optional
from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.api.auth.schemas import TokenData
from app.api.user.dependencies import UserServiceDep
from app.api.mail.dependencies import MailServiceDep
from app.core.settings import settings
from app.core.logger import setup_logger

from .service import AuthService

logger = setup_logger("AuthDependencies")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_none = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_auth_service(
    user_service: UserServiceDep,
    mail_service: MailServiceDep,
):
    return AuthService(user_service, mail_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def authenticate(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Validate required fields
        if not all(key in payload for key in ("sub", "exp", "email")):
            raise credentials_exception

        # Check token expiration
        exp_timestamp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if exp_timestamp < datetime.now(timezone.utc):
            raise credentials_exception

        # Convert payload to TokenData
        token_data = TokenData(
            sub=payload["sub"],
            email=payload["email"],
        )

        return token_data

    except InvalidTokenError:
        raise credentials_exception


def authenticate_or_none(
    token: Annotated[Optional[str], Depends(oauth2_scheme_none)],
) -> Optional[TokenData]:
    if token is None:
        return None
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Validate required fields
        if not all(key in payload for key in ("sub", "exp", "email")):
            return None

        # Check token expiration
        exp_timestamp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if exp_timestamp < datetime.now(timezone.utc):
            return None

        # Convert payload to TokenData
        token_data = TokenData(
            sub=payload["sub"],
            email=payload["email"],
        )

        return token_data

    except InvalidTokenError:
        return None


def authenticate_http(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    return authenticate(token)


async def authenticate_websocket(websocket: WebSocket) -> TokenData:
    try:
        token = websocket.query_params.get("access_token")
        if not token:
            await websocket.close(code=1008, reason="Missing authentication token")
            logger.error("Missing authentication token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
            )

        return authenticate(token)
    except HTTPException:
        await websocket.close(code=1008, reason="Invalid authentication token")
        logger.error("Invalid authentication token")
        raise
    except Exception as e:
        await websocket.close(code=1011, reason="Internal server error")
        logger.error(f"Internal server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


AuthenticateDep = Annotated[TokenData, Depends(authenticate_http)]
AuthenticateOrNoneDep = Annotated[TokenData | None, Depends(authenticate_or_none)]
AuthenticateWebsocketDep = Annotated[TokenData, Depends(authenticate_websocket)]
