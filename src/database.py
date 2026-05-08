import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

engine=create_async_engine(os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:admin@localhost:5434/library_db"),echo=True)

new_session=async_sessionmaker(engine, expire_on_commit=False)
    
async def get_session():
    async with new_session() as session:
        yield session
            
class Base(DeclarativeBase):
    metadata = MetaData()
    pass