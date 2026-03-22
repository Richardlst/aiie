from sqlmodel import select
from typing import Optional
from app.api.user.models import User
from app.core.repository import BaseRepository
from sqlmodel.ext.asyncio.session import AsyncSession


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return (await self.session.exec(statement)).first()
