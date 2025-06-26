# db/schemas.py
from pydantic import BaseModel


class VideoBase(BaseModel):
    title: str
    uploader: str
    upload_date: str
    view_count: int
    video_url: str
    thumbnail_url: str
    local_thumbnail_path: str
    format: str
    duration: int


class VideoRead(BaseModel):
    id: str
    title: str
    uploader: str
    upload_date: str
    view_count: int
    video_url: str
    thumbnail_url: str
    local_thumbnail_path: str
    format: str
    duration: int

    class Config:
        orm_mode = True  # ✅ 這一行很重要！
