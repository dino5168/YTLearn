from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

note_router = APIRouter(prefix="/note", tags=["note"])

STORY_DIR = (
    "C:/ytdb/users_data/0000000029/Note/20250715_153817"  # 你原本設定的 STORY_DIR
)


# 回傳 mp3 檔案
@note_router.get("/mp3/{filename}", response_class=FileResponse)
async def get_story_file(filename: str):
    file_path = os.path.join(STORY_DIR, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


# 回傳字幕檔
@note_router.get("/srt/{filename}", response_class=FileResponse)
async def get_srt_file(filename: str):
    file_path = os.path.join(STORY_DIR, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Subtitle file not found")

    return FileResponse(
        path=file_path,
        media_type="text/plain",  # 或 "application/x-subrip"
        filename=filename,
    )
