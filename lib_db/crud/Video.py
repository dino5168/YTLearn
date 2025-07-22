# lib_db/crud.py

from sqlalchemy.orm import Session
from lib_db.models.Video import Video


def get_video(db: Session, video_id: str):
    return db.query(Video).filter(Video.Video.id == video_id).first()


# 取得 Video
def get_video_list(db: Session, skip: int = 0, limit: int = 10):
    print("正在查詢視頻列表...")
    videos = db.query(Video).all()
    # videos = db.query(Video).filter(Video.category == "Music").all()

    print("總共有多少影片？", len(videos))
    return videos
    # return db.query(Video).offset(skip).limit(limit).all()
