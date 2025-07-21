from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    Numeric,
    Float,
    BigInteger,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Videos(Base):
    __tablename__ = "videos"
    id = Column(Text, primary_key=True, index=True)  # 影片ID
    title = Column(Text, nullable=True)  # 影片標題
    uploader = Column(Text, nullable=True)  # 上傳者
    upload_date = Column(Date, nullable=True)  # 上傳日期
    view_count = Column(Integer, nullable=True)  # 觀看次數
    video_url = Column(Text, nullable=True)  # 影片連結
    thumbnail_url = Column(Text, nullable=True)  # 影片標題
    local_thumbnail_path = Column(Text, nullable=True)  # 影片圖像本機位置
    format = Column(Text, nullable=True)  # 影片格式
    duration = Column(Integer, nullable=True)  # 影片長度
    user_id = Column(Integer, nullable=True)
    lan = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
