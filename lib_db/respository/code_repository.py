# repository/code_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List, Optional
from lib_db.models.code import code  # 確保這個 import 路徑正確


class CodeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[code]:
        result = await self.db.execute(select(code).order_by(code.sort_order))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Optional[code]:
        result = await self.db.execute(select(code).where(code.id == id))
        return result.scalar_one_or_none()

    async def get_by_category(self, category: str) -> List[code]:
        result = await self.db.execute(
            select(code)
            .where(code.category == category, code.is_active == True)
            .order_by(code.sort_order)
        )
        return result.scalars().all()

    async def create(self, data: dict) -> code:
        new_code = code(**data)
        self.db.add(new_code)
        await self.db.flush()  # 或 commit 視情況
        return new_code

    async def update(self, id: int, data: dict) -> Optional[code]:
        result = await self.db.execute(select(code).where(code.id == id))
        db_code = result.scalar_one_or_none()
        if not db_code:
            return None

        for key, value in data.items():
            setattr(db_code, key, value)

        await self.db.flush()
        return db_code

    async def delete(self, id: int) -> bool:
        result = await self.db.execute(select(code).where(code.id == id))
        db_code = result.scalar_one_or_none()
        if not db_code:
            return False

        await self.db.delete(db_code)
        return True
