# api/start_message.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging


from api.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時
    for key, value in settings.model_dump().items():
        logger.info(f"{key} = {value}")

    logger.info("🚀 FastAPI 服務器啟動成功!")
    logger.info("📍 服務器地址: http://127.0.0.1:8000")
    logger.info("📖 API 文檔: http://127.0.0.1:8000/docs")
    logger.info(settings.JWT_SECRET_KEY)
    yield
    # 關閉時
    logger.info("👋 FastAPI 服務器關閉")
