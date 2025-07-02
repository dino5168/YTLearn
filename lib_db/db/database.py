# lib_db/db/database.py

import psycopg2  # 同步 PostgreSQL 驅動
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker

from app.config import settings

# 同步資料庫連線字串
DATABASE_URL = settings.DB_CONNECT_STRING  # e.g., postgresql://user:pass@localhost/db
# 非同步資料庫連線字串（使用 asyncpg 驅動）
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# --- 同步 SQLAlchemy 設定 ---
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 非同步 SQLAlchemy 設定 ---
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# --- Base 共享模型宣告基礎 ---
Base = declarative_base()


# --- 同步 Session Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 非同步 Session Dependency ---
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
