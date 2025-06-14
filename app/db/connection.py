import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# On Railway these are set for you; locally you can populate them via a .env and python-dotenv if you like.
USER     = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST     = os.getenv("PGHOST")
PORT     = os.getenv("PGPORT")
DB       = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB")

if not all([USER, PASSWORD, HOST, PORT, DB]):
    raise RuntimeError(
        "Missing one of PGUSER/PGPASSWORD/PGHOST/PGPORT/PGDATABASE env-vars"
    )

DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

# 1) Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,   # set True if you want SQL logged
    future=True,  # use SQLAlchemy 2.x style
)

# 2) Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# 3) Base class for your ORM models
Base = declarative_base()

# 4) FastAPI dependency to get a session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

print("✅ Connected to database:", DATABASE_URL)
