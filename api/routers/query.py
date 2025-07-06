# 路由設定 與檔名命名 有問題 ...
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from lib_db.db.database import get_async_db

# from lib_util.Auth import get_current_user  # Import the dependency
from typing import List, Optional, Dict, Any
from fastapi import Body
from lib_sql.SQLLoader import SQLLoader
from lib_sql.SQLQueryExecutor import SQLQueryExecutor

from lib_sql.sql_loader_singleton import get_sql_loader

sql_loader = get_sql_loader()
query_router = APIRouter(prefix="/DBQuery", tags=["DBQuery"])


@query_router.get("/{sql_key}")
async def query_get(
    sql_key: str,
    id: Optional[int] = None,
    ids: Optional[List[int]] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    # 直接使用全域實例，不需要重複建立
    executor = SQLQueryExecutor(sql_loader, db)

    params = {}
    if id is not None:
        params["id"] = id
    if ids:
        params["ids"] = ids

    result = await executor.execute(sql_key, params)
    return result


@query_router.post("/{sql_key}")
async def query_post(
    sql_key: str,
    params: Optional[Dict[str, Any]] = Body(default_factory=dict),
    db: AsyncSession = Depends(get_async_db),
):
    sql_loader = SQLLoader()
    executor = SQLQueryExecutor(sql_loader, db)

    result = await executor.execute(sql_key, params)
    return result


@query_router.get("/TableSchema/{sql_key}")
async def query_get(
    sql_key: str,
    table_name: str = Query(..., description="要查詢的資料表名稱"),
    db: AsyncSession = Depends(get_async_db),
):
    print(table_name)
    # 直接使用全域實例，不需要重複建立
    executor = SQLQueryExecutor(sql_loader, db)
    params = {"table_name": table_name}
    result = await executor.execute(sql_key, params)
    return result
