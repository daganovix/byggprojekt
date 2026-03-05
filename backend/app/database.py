import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import Base

_raw = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./construction_projects.db")

# Railway (and some providers) give postgres:// — SQLAlchemy needs postgresql+asyncpg://
if _raw.startswith("postgres://"):
    _raw = _raw.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw.startswith("postgresql://") and "+asyncpg" not in _raw:
    _raw = _raw.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = _raw

_is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    # SQLite needs check_same_thread=False; Postgres does not support it
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
