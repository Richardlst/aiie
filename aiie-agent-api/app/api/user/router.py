from fastapi import APIRouter

from app.api.auth.dependencies import AuthServiceDep, AuthenticateDep
from app.api.user.dependencies import UserServiceDep
from app.api.user.schemas import UserResponse, UserUpdatePub

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("", response_model=UserResponse)
async def get_current_user(
    user_service: UserServiceDep,
    token_data: AuthenticateDep,
):
    return await user_service.get_by_id(id=token_data.sub)


@user_router.put("", response_model=UserResponse)
async def update_user(
    user_update: UserUpdatePub,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    token_data: AuthenticateDep,
):
    hashed_password = auth_service.get_password_hash(user_update.password)
    user_update.password = hashed_password
    return await user_service.update(id=token_data.sub, user=user_update)
