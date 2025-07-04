# 新增資料使用
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from lib_db.db.database import get_async_db

# from lib_util.Auth import get_current_user  # Import the dependency
from typing import List, Optional, Dict, Any
from fastapi import Body
from lib_sql.SQLLoader import SQLLoader
from lib_sql.SQLQueryExecutor import SQLQueryExecutor

from lib_sql.sql_loader_singleton import get_sql_loader

create_router = APIRouter(prefix="/DBCreate", tags=["DBCreate"])

sql_loader = get_sql_loader()


@create_router.post("/tableComment")
async def set_column_comment(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_async_db),
):
    table_name = payload.get("table_name")
    column_name = payload.get("column_name")
    comment = payload.get("comment")
    print(table_name)
    print(column_name)
    print(comment)

    # 安全檢查，避免 SQL Injection
    if not (table_name and column_name and isinstance(comment, str)):
        return {"error": "Missing required fields"}

    if not table_name.isidentifier() or not column_name.isidentifier():
        return {"error": "Invalid table or column name"}
    # COMMENT ON COLUMN table_name.column_name IS '你的描述文字';

    # 組合 SQL
    sql = f"COMMENT ON COLUMN {table_name}.{column_name} IS '{comment}'"
    print(sql)

    try:
        await db.execute(text(sql), {"comment": comment})
        await db.commit()
        return {
            "success": True,
            "message": f"Set comment on {table_name}.{column_name}",
        }
    except Exception as e:
        await db.rollback()
        return {"success": False, "error": str(e)}
