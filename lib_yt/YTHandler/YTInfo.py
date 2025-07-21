from datetime import datetime
from sqlalchemy import select
from yt_dlp import YoutubeDL

from lib_db.models.Video import Video
from lib_db.db.database import AsyncSessionLocal


# 取得影片資訊
async def fetch_info(url: str):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return info


# 資料欄位定義不一致需要資料
def map_info_to_video(info: dict, user_id: int = None) -> Video:
    upload_date = None
    if "upload_date" in info and info["upload_date"]:
        try:
            upload_date = datetime.strptime(info["upload_date"], "%Y%m%d").date()
        except ValueError:
            pass

    return Video(
        id=info.get("id"),
        title=info.get("title"),
        uploader=info.get("uploader"),
        upload_date=upload_date,
        view_count=info.get("view_count"),
        video_url=info.get("webpage_url"),
        thumbnail_url=info.get("thumbnail"),
        local_thumbnail_path=None,  # 可自行處理下載並設定
        format=info.get("format"),
        duration=info.get("duration"),
        user_id=user_id,
        lan=info.get("language"),
        category=(info.get("categories") or [None])[0],
    )


async def save_video_to_db(info: dict, user_id: int = None) -> Video:
    async with AsyncSessionLocal() as db:
        video_entry = map_info_to_video(info, user_id)
        db.add(video_entry)
        await db.commit()
        return video_entry


async def query_video_byid(video_id: str) -> Video:
    async with AsyncSessionLocal() as db:
        stmt = select(Video).where(Video.id == video_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
