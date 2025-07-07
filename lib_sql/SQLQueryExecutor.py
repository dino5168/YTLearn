from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from lib_sql import SQLLoader
import re


class SQLQueryExecutor:
    def __init__(self, sql_loader: SQLLoader, db_session: AsyncSession):
        self.sql_loader = sql_loader
        self.db = db_session

    async def execute(
        self,
        sql_key: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        # 取得 SQL 字串

        sql_raw = self.sql_loader.get_sql(sql_key)

        if not sql_raw:
            raise KeyError(f"SQL key '{sql_key}' not found.")

        sql_text_obj = text(sql_raw)

        # 處理 expanding list
        if params:
            for k, v in params.items():
                if isinstance(v, list):
                    sql_text_obj = sql_text_obj.bindparams(bindparam(k, expanding=True))
        # 執行 SQL
        result = await self.db.execute(sql_text_obj, params or {})

        # 判斷是否為 SELECT
        is_select = bool(re.match(r"^\s*SELECT", sql_raw, re.IGNORECASE))
        is_insert = bool(re.match(r"^\s*INSERT", sql_raw, re.IGNORECASE))

        if is_select:
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        else:
            await self.db.commit()  # 非 select 需 commit
            # 如果是 INSERT，嘗試取得新插入的 ID
            if is_insert:
                inserted_row = result.fetchone()
                inserted_id = inserted_row[0] if inserted_row else None
                return {
                    "rows_affected": result.rowcount,
                    "inserted_id": inserted_id,  # 新插入記錄的 ID
                    "operation": "INSERT",
                    "success": result.rowcount > 0,
                }
            else:
                return {
                    "rows_affected": result.rowcount,
                    "operation": "UPDATE/DELETE",
                    "success": result.rowcount > 0,
                }
