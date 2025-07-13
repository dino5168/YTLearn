# api/config.py
# 讀取 .evn 檔案並設定靜態路徑
from pydantic_settings import BaseSettings  # ✅ 正確寫法（v2 專用）
from pathlib import Path


class Settings(BaseSettings):
    DEBUG: bool = False
    THUMBNAILS_DIR: Path
    THUMBNAILS_URL_PATH: str = "/thumbnails"

    SRT_DIR: Path
    SRT_URL_PATH: str = "/srt"

    YT_WATCH_URL: str = "https://www.youtube.com/watch?v="
    BASE_DIR: Path
    JWT_SECRET_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    FRONTEND_URL: str
    JWT_EXPIRE_HOURS: int
    GOOGLE_CALL_BACK_URL: str
    GOOGLE_REDIRECT_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    FRONTEDN_GOOGLE_SUCCESS: str
    CORS_ALLOW: str = "http://127.0.0.1:3000"
    DB_CONNECT_STRING: str = "postgresql://postgres:0936284791@localhost:5432/videos"
    UPLOAD_DIR: Path  # 預設上傳目錄
    TTS_DIR: Path  # 語音合成目錄

    SAMPLE_VOICE_URL: str = "/sample_voice"  # 樣本語音 URL 路徑
    SAMPLE_VOICE_DIR: Path  # 樣本語音目錄

    #  郵件設定
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587  # 郵件伺服器端口
    EMAIL_PASSWORD: str = ""  # 郵件密碼
    EMAIL_FROM: str = ""  # 郵件發件人地址
    EMAIL_VERIFY_DOMAIN: str = "http://localhost:3000"  # 替換為你的域名
    ADMIN_EMAIL: str
    #
    STORY_DIR: Path = "c:/ytdb/story"
    STORY_URL: str

    class Config:
        env_file = ".env"  # 指定 .env 檔案路徑


settings = Settings()
