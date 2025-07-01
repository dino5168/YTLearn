from sqlalchemy import Column, Integer, String
from lib_db.db.database import Base


class Subtitle(Base):
    __tablename__ = "subtitles"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)  # YouTube 影片 ID
    seq = Column(Integer)  # 字幕序號
    start_time = Column(String)  # 開始時間，例如 "00:00:01,000"
    end_time = Column(String)  # 結束時間，例如 "00:00:04,000"
    en_text = Column(String)  # 英文字幕內容
    zh_text = Column(String)  # 中文字幕內容

    def __repr__(self):
        return f"<Subtitle video_id={self.video_id} seq={self.seq}>"
