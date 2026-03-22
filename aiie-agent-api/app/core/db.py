from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from urllib.parse import quote_plus

from .tables import *  # noqa
from .settings import settings

# Encode the password to avoid special characters issues
encoded_password = quote_plus(settings.DB_PASSWORD)
db_url = f"postgresql+asyncpg://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

async_engine = create_async_engine(
    db_url,
    connect_args={
        "timeout": 10, 
        "command_timeout": 60, 
    },
)


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
