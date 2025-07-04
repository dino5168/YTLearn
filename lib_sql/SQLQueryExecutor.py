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

        if is_select:
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        else:
            # 非 SELECT（例如 INSERT/UPDATE/DELETE），可選擇回傳影響筆數
            await self.db.commit()  # INSERT 一定要 commit
            return {"rows_affected": result.rowcount}
