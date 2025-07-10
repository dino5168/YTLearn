import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Any


def load_json_data(json_filepath: str) -> Dict[str, Any]:
    """載入 JSON 檔案"""
    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到檔案：{json_filepath}")
    except json.JSONDecodeError:
        raise ValueError(f"JSON 格式錯誤：{json_filepath}")


def connect_to_database(
    host: str, database: str, user: str, password: str, port: int = 5432
):
    """連接到 PostgreSQL 資料庫"""
    try:
        conn = psycopg2.connect(
            host=host, database=database, user=user, password=password, port=port
        )
        return conn
    except psycopg2.Error as e:
        raise ConnectionError(f"資料庫連接失敗：{e}")


def insert_subtitles_to_db(json_filepath: str, db_config: Dict[str, str]):
    """將 JSON 字幕資料插入資料庫"""

    # 載入 JSON 資料
    data = load_json_data(json_filepath)
    video_id = data.get("video_id")
    subtitles = data.get("subtitles", [])

    if not video_id:
        raise ValueError("JSON 中缺少 video_id")

    if not subtitles:
        raise ValueError("JSON 中缺少 subtitles 資料")

    # 連接資料庫
    conn = connect_to_database(**db_config)

    try:
        with conn.cursor() as cursor:
            # 準備 INSERT 語句
            insert_query = """
                INSERT INTO subtitles (video_id, seq, start_time, end_time, en_text, zh_text) 
                VALUES (%(video_id)s, %(seq)s, %(start_time)s, %(end_time)s, %(en_text)s, %(zh_text)s)
            """

            # 批次插入資料
            insert_data = []
            for subtitle in subtitles:
                insert_data.append(
                    {
                        "video_id": video_id,
                        "seq": subtitle.get("seq"),
                        "start_time": subtitle.get("start_time"),
                        "end_time": subtitle.get("end_time"),
                        "en_text": subtitle.get("ex_text"),  # 注意：JSON 中是 ex_text
                        "zh_text": subtitle.get("zh_text"),
                    }
                )

            # 執行批次插入
            cursor.executemany(insert_query, insert_data)

            # 提交事務
            conn.commit()

            print(f"✅ 成功插入 {len(insert_data)} 筆字幕資料")
            print(f"📹 影片 ID：{video_id}")

    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"資料庫操作失敗：{e}")

    finally:
        conn.close()


def create_table_if_not_exists(db_config: Dict[str, str]):
    """如果資料表不存在則建立"""
    conn = connect_to_database(**db_config)

    try:
        with conn.cursor() as cursor:
            create_table_query = """
                CREATE TABLE IF NOT EXISTS subtitles (
                    id SERIAL PRIMARY KEY,
                    video_id VARCHAR(255) NOT NULL,
                    seq INTEGER NOT NULL,
                    start_time VARCHAR(12) NOT NULL,
                    end_time VARCHAR(12) NOT NULL,
                    en_text TEXT,
                    zh_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(video_id, seq)
                );
            """

            cursor.execute(create_table_query)
            conn.commit()
            print("✅ 資料表檢查/建立完成")

    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"建立資料表失敗：{e}")

    finally:
        conn.close()


# 使用範例
# DB_CONNECT_STRING="postgresql://postgres:0936284791@localhost:5432/videos"
if __name__ == "__main__":
    # 資料庫設定
    DB_CONFIG = {
        "host": "localhost",
        "database": "videos",
        "user": "postgres",
        "password": "0936284791",
        "port": 5432,
    }

    # 也可以從環境變數讀取
    # DB_CONFIG = {
    #     'host': os.getenv('DB_HOST', 'localhost'),
    #     'database': os.getenv('DB_NAME', 'your_database'),
    #     'user': os.getenv('DB_USER', 'your_user'),
    #     'password': os.getenv('DB_PASSWORD', 'your_password'),
    #     'port': int(os.getenv('DB_PORT', 5432))
    # }

    try:
        # 建立資料表（如果不存在）
        create_table_if_not_exists(DB_CONFIG)

        # 插入資料
        insert_subtitles_to_db("c:/temp/b/Lady_combined.json", DB_CONFIG)

    except Exception as e:
        print(f"❌ 錯誤：{e}")
