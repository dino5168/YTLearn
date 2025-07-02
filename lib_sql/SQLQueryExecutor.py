from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, bindparam
from typing import Optional, Dict, Any, List
from lib_sql import SQLLoader


class SQLQueryExecutor:
    def __init__(self, sql_loader: SQLLoader, db_session: AsyncSession):
        self.sql_loader = sql_loader
        self.db = db_session

    async def execute(
        self,
        sql_key: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        # 取得 SQL 字串
        sql_raw = self.sql_loader.get_sql(sql_key)

        if not sql_raw:
            raise KeyError(f"SQL key '{sql_key}' not found.")

        # 建立 SQLAlchemy text 物件
        sql_text = text(sql_raw)

        # 處理 list 參數 (IN 查詢)
        if params:
            for k, v in params.items():
                if isinstance(v, list):
                    sql_text = sql_text.bindparams(bindparam(k, expanding=True))

        # 綁定參數
        if params:
            result = await self.db.execute(sql_text, params)
        else:
            result = await self.db.execute(sql_text)

        rows = result.fetchall()

        # 回傳 List[Dict]
        return [dict(row._mapping) for row in rows]
