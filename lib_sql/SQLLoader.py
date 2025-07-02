# lib/sql_loader.py
import json
import yaml  # <--- 加入 yaml 支援
from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict


@lru_cache(maxsize=1)
def load_all_sqls(sql_dir: str = "sql") -> Dict[str, str]:
    """
    使用 lru_cache 確保只讀取一次 SQL JSON / YAML 檔案
    支援 .sql.json、.sql.yaml、.sql.yml
    """
    print("⚡ 實際讀取 SQL 設定檔案一次")
    sql_map = {}
    sql_path = Path(sql_dir)

    if not sql_path.exists():
        print(f"⚠️  SQL 目錄不存在: {sql_dir}")
        return sql_map

    # 支援的檔案格式
    patterns = ["*.sql.json", "*.sql.yaml", "*.sql.yml"]

    for pattern in patterns:
        for path in sql_path.glob(pattern):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    if path.suffix == ".json":
                        content = json.load(f)
                    else:
                        content = yaml.safe_load(f)

                    if not isinstance(content, dict):
                        print(f"⚠️  檔案格式錯誤（需為字典）: {path.name}")
                        continue

                    sql_map.update(content)
                    print(f"✅ 載入 SQL 檔案: {path.name}")
            except Exception as e:
                print(f"❌ 載入 SQL 檔案失敗: {path.name}, 錯誤: {e}")

    print(f"📊 總共載入 {len(sql_map)} 個 SQL 查詢")
    return sql_map


class SQLLoader:
    def __init__(self, sql_dir: str = "sql"):
        self.sql_dir = sql_dir
        # 使用快取函數，確保只讀取一次
        self._sqls = load_all_sqls(sql_dir)

    def get_sql(self, key: str) -> str:
        """
        取得指定 key 的 SQL 查詢

        Args:
            key: SQL 查詢的 key 名稱

        Returns:
            str: SQL 查詢字串

        Raises:
            KeyError: 當找不到指定的 key 時
        """
        if key not in self._sqls:
            available_keys = list(self._sqls.keys())
            raise KeyError(
                f"SQL key '{key}' not found. " f"Available keys: {available_keys}"
            )
        return self._sqls[key]

    def list_available_keys(self) -> list:
        """回傳所有可用的 SQL key"""
        return list(self._sqls.keys())

    def reload(self):
        """重新載入 SQL 檔案（清除快取）"""
        load_all_sqls.cache_clear()
        self._sqls = load_all_sqls(self.sql_dir)
        print("🔄 SQL 檔案已重新載入")


# ✅ CLI 測試：讓你可以直接執行這個檔案驗證功能
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SQLLoader 測試工具")
    parser.add_argument("key", type=str, nargs="?", help="SQL 查詢的 key 名稱")
    parser.add_argument(
        "--dir", type=str, default="sql", help="SQL 資料夾路徑 (預設為 sql/)"
    )
    parser.add_argument("--list", action="store_true", help="列出所有可用的 SQL keys")

    args = parser.parse_args()

    loader = SQLLoader(sql_dir=args.dir)

    if args.list:
        keys = loader.list_available_keys()
        print(f"📝 可用的 SQL keys ({len(keys)} 個):")
        for key in sorted(keys):
            print(f"  - {key}")
    elif args.key:
        try:
            sql = loader.get_sql(args.key)
            print(f"✔ 找到 SQL：[{args.key}]\n{sql}")
        except KeyError as e:
            print(f"❌ {e}")
    else:
        print("請提供 SQL key 或使用 --list 參數查看所有可用的 keys")
