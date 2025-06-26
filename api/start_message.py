# api/start_message.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時
    logger.info("🚀 FastAPI 服務器啟動成功!")
    logger.info("📍 服務器地址: http://127.0.0.1:8000")
    logger.info("📖 API 文檔: http://127.0.0.1:8000/docs")
    yield
    # 關閉時
    logger.info("👋 FastAPI 服務器關閉")
