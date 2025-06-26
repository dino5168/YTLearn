# api/config.py
# 讀取 .evn 檔案並設定靜態路徑
from pydantic_settings import BaseSettings  # ✅ 正確寫法（v2 專用）
from pathlib import Path


class Settings(BaseSettings):
    THUMBNAILS_DIR: Path
    THUMBNAILS_URL_PATH: str = "/thumbnails"

    SRT_DIR: Path
    SRT_URL_PATH: str = "/srt"

    YT_WATCH_URL: str = "https://www.youtube.com/watch?v="
    BASE_DIR: Path

    class Config:
        env_file = ".env"  # 指定 .env 檔案路徑


settings = Settings()
