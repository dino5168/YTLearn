from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import PlainTextResponse

from lib_db.db.database import SessionLocal
from lib_db.schemas.Subtitle import SubtitleCreate, SubtitleInDB, SubtitleUpdate
from lib_db.crud.subtitle_crud import get_subtitles_by_video

# from lib_db.crud.subtitle_crud import subtitle_crud  # ✅ 匯入這個檔案（不是 Subtitle）
import lib_db.crud.subtitle_crud as subtitle_crud

subtitle_router = APIRouter(
    prefix="/subtitles",
    tags=["Subtitles"],
)


# Dependency: 提供 DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@subtitle_router.get("/{video_id}")
def get_subtitle_json(video_id: str, db: Session = Depends(get_db)):
    print(f"video_id: {video_id}")
    subtitles = get_subtitles_by_video(db, video_id)
    if not subtitles:
        raise HTTPException(status_code=404, detail="No subtitles found for the video.")

    result = []
    for s in subtitles:
        result.append(
            {
                "seq": s.seq,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "en_text": s.en_text.strip(),
                "zh_text": s.zh_text.strip(),
            }
        )

    return result  # FastAPI 會自動回傳 JSON 格式


@subtitle_router.post("/", response_model=SubtitleInDB)
def create_sub(sub: SubtitleCreate, db: Session = Depends(get_db)):
    return subtitle_crud.create_subtitle(db, sub)


@subtitle_router.get("/video/{video_id}", response_model=list[SubtitleInDB])
def read_subs_by_video(video_id: str, db: Session = Depends(get_db)):
    return subtitle_crud.get_subtitles_by_video(db, video_id)


# API 路由示例
# @app.put("/subtitles/", response_model=Subtitle)
# def update_subtitle_endpoint(
#     subtitle_update: SubtitleUpdate,
#     db: Session = Depends(get_db)
# ):
#     """更新字幕 - 使用 video_id 和 seq 作为查询条件"""
#     subtitle = update_subtitle_from_body(db, subtitle_update)
#     if subtitle is None:
#         raise HTTPException(status_code=404, detail="字幕记录未找到")
#     return subtitle


@subtitle_router.put("/{subtitle_id}", response_model=SubtitleInDB)
def update_sub(
    subtitle_id: int, subtitle: SubtitleUpdate, db: Session = Depends(get_db)
):
    # ✅ 列出用戶上傳的資料
    print("使用者送出的 subtitle_id:", subtitle_id)
    print("使用者送出的更新資料:", subtitle.dict())

    updated = subtitle_crud.update_subtitle(db, subtitle_id, subtitle)
    if not updated:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return updated


# 方案1：使用 video_id 和 seq 作为路径参数（推荐）
@subtitle_router.put("/{video_id}/{seq}", response_model=SubtitleInDB)
def update_sub_by_video_seq(
    video_id: str, seq: int, subtitle: SubtitleUpdate, db: Session = Depends(get_db)
):
    """根据 video_id 和 seq 更新字幕"""
    print(f"使用者送出的 video_id: {video_id}, seq: {seq}")
    print("使用者送出的更新資料:", subtitle.dict())

    updated = subtitle_crud.update_subtitle_by_video_seq(db, video_id, seq, subtitle)
    if not updated:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return updated


@subtitle_router.delete("/{subtitle_id}")
def delete_sub(subtitle_id: int, db: Session = Depends(get_db)):
    success = subtitle_crud.delete_subtitle(db, subtitle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return {"status": "deleted"}
