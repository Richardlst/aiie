from fastapi import Depends
from typing import Annotated

from app.api.auth_google.service import GoogleAuthService
from app.api.user.dependencies import UserServiceDep
from app.api.auth.dependencies import AuthServiceDep

def get_google_auth_service(
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
):
    return GoogleAuthService(user_service, auth_service)


GoogleAuthServiceDep = Annotated[GoogleAuthService, Depends(get_google_auth_service)]
