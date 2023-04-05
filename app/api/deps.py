from typing import Generator, AsyncGenerator

from app.db.session import SessionLocal
from app.db.session import async_session


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def async_get_db() -> AsyncGenerator:
    async with async_session() as session:
        yield session
