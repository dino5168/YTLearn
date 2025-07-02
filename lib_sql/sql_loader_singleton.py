from lib_sql.SQLLoader import SQLLoader
from typing import Optional


class SQLLoaderSingleton:
    """SQLLoader 單例模式"""

    _instance: Optional[SQLLoader] = None
    _sql_dir: Optional[str] = None

    @classmethod
    def get_instance(cls, sql_dir: str = "lib_sql/sql") -> SQLLoader:
        """取得 SQLLoader 單例實例"""
        if cls._instance is None or cls._sql_dir != sql_dir:
            print(f"🏗️  建立 SQLLoader 單例實例: {sql_dir}")
            cls._instance = SQLLoader(sql_dir=sql_dir)
            cls._sql_dir = sql_dir
        return cls._instance

    @classmethod
    def reload(cls):
        """重新載入 SQL 檔案"""
        if cls._instance:
            cls._instance.reload()


# 全域函數，方便使用
def get_sql_loader(sql_dir: str = "lib_sql/sql") -> SQLLoader:
    """取得全域 SQLLoader 實例"""
    return SQLLoaderSingleton.get_instance(sql_dir)
