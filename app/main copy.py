# main.py
import logging
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from api.video.routes import router as video_router  # 匯入你的子路由
from api.routers.Subtitle import subtitle_router  # 匯入你的子路由
from api.routers.Admin import admin_router

# from api.routers.Transcribe import transcribe_router

from api.static_path.static_config import mount_static  # 靜態路徑
from api.start_message import lifespan  # ✅ 引入 lifespan 顯示 啟動訊息

from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from lib_db.db.database_lite import SessionLocal, engine

# from lib_db import models, crud, schemas

from api.config import settings  # 讀取設定檔
from middlewares.cors import setup_cors  # ✅ CORS 設定模組


from lib_db.crud.subtitle_crud import get_subtitles_by_video

THUMBNAILS_DIR = settings.THUMBNAILS_DIR
THUMBNAILS_URL_PATH = settings.THUMBNAILS_URL_PATH
# ✅ 傳入 lifespan！
app = FastAPI(
    title="視頻管理 API", description="視頻管理 API", version="1.0.0", lifespan=lifespan
)

# 掛載 /videos 路由
app.include_router(video_router)
app.include_router(subtitle_router)
app.include_router(admin_router)
# app.include_router(transcribe_router)
# ⬅ 掛載靜態資源
mount_static(app)
# ✅ 掛載靜態文件目錄

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def format_srt(subtitles) -> str:
    lines = []
    for i, s in enumerate(subtitles, start=1):
        start = s.start_time  # 直接使用字串
        end = s.end_time  # 直接使用字串

        en_text = s.en_text.strip()
        zh_text = s.zh_text.strip()

        content = "\n".join(filter(None, [en_text, zh_text]))
        lines.append(f"{i}\n{start} --> {end}\n{content}\n")

    return "\n".join(lines)


# 取得資料庫連線
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/subtitle/{video_id}", response_class=PlainTextResponse)
def get_subtitle_srt(video_id: str, db: Session = Depends(get_db)):
    print(f"video_id:{video_id}")
    subtitles = get_subtitles_by_video(db, video_id)
    if not subtitles:
        raise HTTPException(status_code=404, detail="No subtitles found for the video.")

    srt_text = format_srt(subtitles)
    return srt_text


# 掛載路由器
app.include_router(router)  # <== 一定要這行！

# ✅ 加入 CORS
setup_cors(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# http://localhost:8000/srt/3geEVwzLj8A.en.srt
# http://localhost:8000/srt/3geEVwzLj8A.en.srt
