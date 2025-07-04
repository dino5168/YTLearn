from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from lib_db.db.database import get_db  # 你定義的 get_db function

from lib_sql.sql_loader_singleton import get_sql_loader
from lib_sql.SQLQueryExecutor import SQLQueryExecutor
from lib_db.db.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

db_update_router = APIRouter(prefix="/DBUpdate", tags=["DBUpdate"])
sql_loader = get_sql_loader()


@db_update_router.put("/TABLE_UPDATE/{sql_key}")
async def test_put(
    sql_key: str, payload: dict = Body(...), db: AsyncSession = Depends(get_async_db)
):
    try:
        executor = SQLQueryExecutor(sql_loader, db)
        result = await executor.execute(sql_key, payload)
        return result
    except Exception as e:
        raise e
