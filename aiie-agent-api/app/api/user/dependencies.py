from app.api.user.service import UserService
from typing import Annotated
from fastapi import Depends

from app.core.dependencies import AsyncSessionDep
from app.api.user.repository import UserRepository


def get_user_repository(session: AsyncSessionDep):
    return UserRepository(session)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
):
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
