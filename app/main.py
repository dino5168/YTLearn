# main.py
import logging
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from api.routers.videos import router as video_router  # 匯入你的子路由
from api.routers.Subtitle import subtitle_router  # 匯入你的子路由
from api.routers.Admin import admin_router
from api.routers.Voice import voice_router
from api.routers.Util import util_router

# auth
from api.routers.auth_google import auth_google
from api.routers.auth_email import auth_email  # 匯入你的子路由

from api.routers.Nav import nav_router
from api.routers.db_query import db_query_router
from api.routers.Common import common_router
from api.routers.db_create import db_create_router
from api.routers.db_delete import db_delete_router

from api.routers.query import query_router
from api.routers.create import create_router
from api.routers.db_update import db_update_router
from api.routers.markdown import markdown_router
from api.routers.Note import note_router
from api.routers.mp4 import mp4_router

# 這個會很耗資源 先 mark 起來
# from api.routers.Transcribe import transcribe_router

#
from app.start_message import lifespan  # ✅ 引入 lifespan 顯示 啟動訊息
from app.config import settings  # 讀取設定檔
from middlewares import IPGeoMiddleware
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
# auth
app.include_router(auth_google)
app.include_router(auth_email)  # 掛載 auth_email 路由
#
app.include_router(db_query_router)
app.include_router(common_router)
# create 2025-07-03
app.include_router(db_create_router)
app.include_router(db_update_router)
app.include_router(db_delete_router)
# mark down
app.include_router(markdown_router)

app.include_router(query_router)
app.include_router(create_router)
# note
app.include_router(note_router)
app.include_router(mp4_router)
# 這個會很耗資源 先 mark 起來
# app.include_router(transcribe_router)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/admin", tags=["admin"])


# 掛載路由器
# app.include_router(router)  # <== 一定要這行！

# ✅ 加入 CORS
setup_cors(app)
# app.add_middleware(IPGeoMiddleware, geoip_db_path=settings.GEOIP_DB_PATH)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# http://localhost:8000/srt/3geEVwzLj8A.en.srt
# http://localhost:8000/srt/3geEVwzLj8A.en.srt
