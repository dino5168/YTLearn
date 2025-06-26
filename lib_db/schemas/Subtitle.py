from pydantic import BaseModel
from typing import Optional


class SubtitleBase(BaseModel):
    video_id: str
    seq: int
    start_time: str
    end_time: str
    en_text: str
    zh_text: str


class SubtitleCreate(SubtitleBase):
    pass  # 跟 Base 一樣（不包含 id）


class SubtitleUpdate(BaseModel):
    """用於更新字幕的 Schema，所有欄位都是可選的"""

    video_id: str  # ❗強制要傳 video_id，其他欄位仍然 Optional
    # video_id: Optional[str] = None
    seq: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    en_text: Optional[str] = None
    zh_text: Optional[str] = None


class SubtitleOut(SubtitleBase):
    id: int  # 包含資料庫自動產生的 id

    class Config:
        orm_mode = True  # 讓 Pydantic 能接收 ORM 物件


# 額外的 Schema，用於不同的使用情境
class SubtitleSearch(BaseModel):
    """用於搜尋字幕的 Schema"""

    video_id: Optional[str] = None
    search_text: Optional[str] = None
    language: Optional[str] = None  # "en", "zh", 或 None (搜尋兩種語言)
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class SubtitleBatch(BaseModel):
    """用於批次操作的 Schema"""

    video_id: str
    subtitles: list[SubtitleCreate]


class SubtitleStats(BaseModel):
    """字幕統計資訊"""

    video_id: str
    total_count: int
    en_text_count: int  # 有英文字幕的數量
    zh_text_count: int  # 有中文字幕的數量
    duration: str  # 總時長


class SubtitleInDB(SubtitleBase):
    id: int
    video_id: str
    seq: int

    class Config:
        # ⚠️ Pydantic V2 建議用 from_attributes
        from_attributes = True
