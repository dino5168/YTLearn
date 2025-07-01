from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from lib_db.db.database import get_db, engine, Base
from lib_db.models.Video import Video


class VideoManager:
    def __init__(self):
        # 創建資料表（如果不存在）
        Base.metadata.create_all(bind=engine)

    def add_or_update_video(self, video_data: Dict[str, Any]):
        """新增或更新影片資料"""
        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            # 檢查影片是否已存在
            existing_video = (
                db.query(Video).filter(Video.id == video_data["id"]).first()
            )

            if existing_video:
                # 更新現有影片
                for key, value in video_data.items():
                    setattr(existing_video, key, value)
            else:
                # 新增影片
                new_video = Video(**video_data)
                db.add(new_video)

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """根據影片 ID 取得影片資料"""
        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                return video.to_dict()
            return None
        finally:
            db.close()

    def video_exists(self, video_id: str) -> bool:
        """檢查影片是否存在"""
        return self.get_video(video_id) is not None

    def delete_video(self, video_id: str):
        """刪除影片"""
        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                db.delete(video)
                db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_all_videos(self) -> list[Dict[str, Any]]:
        """取得所有影片資料"""
        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            videos = db.query(Video).all()
            return [video.to_dict() for video in videos]
        finally:
            db.close()

    def search_videos(self, keyword: str) -> list[Dict[str, Any]]:
        """根據關鍵字搜尋影片標題或上傳者"""
        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            videos = (
                db.query(Video)
                .filter(
                    (Video.title.ilike(f"%{keyword}%"))
                    | (Video.uploader.ilike(f"%{keyword}%"))
                )
                .all()
            )
            return [video.to_dict() for video in videos]
        finally:
            db.close()

    def close(self):
        """保持與原有介面相容，但 PostgreSQL 不需要手動關閉連線"""
        pass
