# api/static_config.py
# 掛載靜態資源到 FastAPI 應用程式
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings  # 讀取設定檔

# 從設定檔取得路徑
THUMBNAILS_DIR = settings.THUMBNAILS_DIR
THUMBNAILS_URL_PATH = settings.THUMBNAILS_URL_PATH

SRT_DIR = settings.SRT_DIR
SRT_URL_PATH = settings.SRT_URL_PATH

# 確保目錄存在
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
SRT_DIR.mkdir(parents=True, exist_ok=True)
#
SAMPLE_VOICE_DIR = settings.SAMPLE_VOICE_DIR
SAMPLE_VOICE_URL = settings.SAMPLE_VOICE_URL
# 確保樣本語音目錄存在
# http://localhost:8000/sample_voice/02_William.mp3


def mount_static(app: FastAPI):
    """掛載 thumbnails 與 srt 靜態目錄到 FastAPI app"""
    app.mount(
        THUMBNAILS_URL_PATH, StaticFiles(directory=THUMBNAILS_DIR), name="thumbnails"
    )
    app.mount(SRT_URL_PATH, StaticFiles(directory=SRT_DIR), name="srt")
    app.mount(
        SAMPLE_VOICE_URL,
        StaticFiles(directory=SAMPLE_VOICE_DIR),
        name="sample_voice",
    )  # 掛載樣本語音目錄
