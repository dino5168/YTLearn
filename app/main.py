# main.py
import logging
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from api.video.routes import router as video_router  # 匯入你的子路由
from api.routers.Subtitle import subtitle_router  # 匯入你的子路由
from api.routers.Admin import admin_router
from api.routers.Voice import voice_router
from api.routers.Util import util_router
from api.routers.auth import auth_router
from api.routers.Nav import nav_router
from api.routers.db_query import db_query_router
from api.routers.Common import common_router
from api.routers.db_create import db_create_router
from api.routers.DataBaseOp import databaseop_router
from api.routers.query import query_router

# 這個會很耗資源 先 mark 起來
# from api.routers.Transcribe import transcribe_router
from app.start_message import lifespan  # ✅ 引入 lifespan 顯示 啟動訊息
from app.config import settings  # 讀取設定檔
from middlewares.cors import setup_cors  # ✅ CORS 設定模組
from api.static_path.static_config import mount_static  # 靜態路徑

# from lib_db import models, crud, schemas


THUMBNAILS_DIR = settings.THUMBNAILS_DIR
THUMBNAILS_URL_PATH = settings.THUMBNAILS_URL_PATH
# ✅ 傳入 lifespan！
app = FastAPI(
    title="視頻管理 API", description="視頻管理 API", version="1.0.0", lifespan=lifespan
)
# ⬅ 掛載靜態資源
mount_static(app)
# ✅ 掛載靜態文件目錄

# 掛載 /videos 路由
app.include_router(nav_router)
app.include_router(video_router)
app.include_router(subtitle_router)
app.include_router(admin_router)
app.include_router(voice_router)
app.include_router(util_router)
app.include_router(auth_router)
app.include_router(db_query_router)
app.include_router(common_router)
app.include_router(db_create_router)
app.include_router(databaseop_router)
app.include_router(query_router)
# app.include_router(transcribe_router)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/admin", tags=["admin"])


# 掛載路由器
# app.include_router(router)  # <== 一定要這行！

# ✅ 加入 CORS
setup_cors(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# http://localhost:8000/srt/3geEVwzLj8A.en.srt
# http://localhost:8000/srt/3geEVwzLj8A.en.srt
