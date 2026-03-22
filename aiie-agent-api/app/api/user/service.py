from typing import Optional, List
import uuid
from fastapi import HTTPException

from app.api.user.repository import UserRepository
from app.api.user.models import User
from app.api.user.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.user_repository.get_by_email(email)

    async def get_by_id(self, id: int) -> Optional[User]:
        return await self.user_repository.find_by_id(id)

    async def get_all(self) -> List[User]:
        return await self.user_repository.find()

    async def create(self, user: UserCreate) -> User:
        new_user = User(**user.model_dump())
        return await self.user_repository.create(obj_in=new_user)

    async def update(self, id: uuid.UUID, user: UserUpdate) -> User:
        db_user = await self.get_by_id(id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        for field, value in user.model_dump(exclude_unset=True).items():
            if hasattr(db_user, field) and (value is not None):
                setattr(db_user, field, value)
        return await self.user_repository.update(obj_in=db_user)

    async def delete(self, id: uuid.UUID) -> None:
        await self.user_repository.delete(id)
