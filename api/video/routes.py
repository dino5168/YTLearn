# api/video/routes.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from lib_db.db.database import SessionLocal, engine
from lib_db.crud import Video
from api.config import settings  # 讀取設定檔


THUMBNAILS_DIR = settings.THUMBNAILS_DIR
THUMBNAILS_URL_PATH = settings.THUMBNAILS_URL_PATH

router = APIRouter(prefix="/videos", tags=["videos"])
# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def read_videos():
    return [{"title": "video1"}]


# 路由匹配會有路由衝突， 這樣可以避免與根路由衝突 須設定優先順序
@router.get("/list")
def read_videos_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # logger.info(f"請求視頻列表，跳過 {skip} 條，限制 {limit} 條")

    try:
        videos = Video.get_video_list(db, skip=skip, limit=limit)

        if not videos:
            logger.warning("沒有找到任何視頻")
            return []

        # ✅ 為每個視頻生成縮圖 URL
        for video in videos:
            thumbnail_filename = f"{video.id}.jpg"  # 或其他格式 .png, .webp
            thumbnail_path = THUMBNAILS_DIR / thumbnail_filename

            if thumbnail_path.exists():
                video.thumbnail_url = (
                    f"http://127.0.0.1:8000{THUMBNAILS_URL_PATH}/{thumbnail_filename}"
                )
            # logger.info(f"使用本地縮圖: {video.thumbnail_url}")
            else:
                logger.info(f"本地縮圖不存在，使用原始 URL: {video.thumbnail_url}")

        logger.info(f"成功返回視頻列表")
        return videos

    except Exception as e:
        logger.error(f"讀取視頻列表時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="內部服務器錯誤")


@router.get("/{video_id}")
def read_video(video_id: str, db: Session = Depends(get_db)):
    logger.info(f"請求視頻 ID: {video_id}")

    try:
        db_video = Video.get_video(db, video_id)
        if db_video is None:
            logger.warning(f"找不到視頻: {video_id}")
            raise HTTPException(status_code=404, detail="Video not found")

        # ✅ 如果有本地縮圖文件，替換 URL
        thumbnail_filename = f"{video_id}.jpg"  # 或其他格式 .png, .webp
        thumbnail_path = THUMBNAILS_DIR / thumbnail_filename

        if thumbnail_path.exists():
            # 生成本地縮圖 URL
            db_video.thumbnail_url = (
                f"http://127.0.0.1:8000{THUMBNAILS_URL_PATH}/{thumbnail_filename}"
            )
            # logger.info(f"使用本地縮圖: {db_video.thumbnail_url}")
        else:
            logger.info(f"本地縮圖不存在，使用原始 URL: {db_video.thumbnail_url}")

        logger.info(f"成功返回視頻: {db_video.title}")
        return db_video

    except Exception as e:
        logger.error(f"讀取視頻時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="內部服務器錯誤")
