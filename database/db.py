import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from dotenv import load_dotenv, find_dotenv 
load_dotenv(find_dotenv())


engine = create_async_engine(url=os.getenv('DATABASE_URL'))
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstact__ = True