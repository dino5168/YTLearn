import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ✅ 連線設定（注意：要用 asyncpg driver）
DB_CONNECT_STRING = "postgresql+asyncpg://postgres:0936284791@localhost:5432/videos"

# ✅ 建立 async engine
engine = create_async_engine(DB_CONNECT_STRING, echo=True)

# ✅ 建立 Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def main():
    async with AsyncSessionLocal() as session:
        # ✅ 查詢資料
        result = await session.execute(text("SELECT id, name, email FROM users"))

        # ✅ 使用 result.mappings() 取得 dict-like 結果（推薦）
        for row in result.mappings():
            print(f"查詢結果: {row['id']}, {row['name']}, {row['email']}")


if __name__ == "__main__":
    asyncio.run(main())
