from sqlalchemy import Column, Integer, String
from lib_db.db.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    uploader = Column(String)
    upload_date = Column(String)
    view_count = Column(Integer)
    video_url = Column(String)
    thumbnail_url = Column(String)
    local_thumbnail_path = Column(String)
    format = Column(String)
    duration = Column(Integer)
