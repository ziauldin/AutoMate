# connection.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Load .env
load_dotenv()

# 2. Read the full DATABASE_URL (e.g. "postgresql+asyncpg://user:pass@host:port/dbname")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Missing DATABASE_URL environment variable")

# 3. Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,    # set True if you want SQL logging
    future=True,
)

# 4. Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 5. Declarative base for your models
Base = declarative_base()

# 6. Dependency for FastAPI endpoints
async def get_db():
    """
    Yields an AsyncSession, rolling back on error.
    Usage:

        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
