from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

note_router = APIRouter(prefix="/note", tags=["note"])


# 回傳 mp3 檔案
BASE_DIR = "C:/ytdb/users_data"


@note_router.get("/mp3/{user_id}/{time_stap}", response_class=FileResponse)
async def get_story_file(user_id: str, time_stap: str):
    filename = "note.mp3"
    safe_user_path = os.path.normpath(
        os.path.join(BASE_DIR, user_id, "Note", time_stap)
    )
    file_path = os.path.normpath(os.path.join(safe_user_path, filename))
    print(file_path)

    if os.path.commonpath([BASE_DIR, file_path]) != os.path.abspath(BASE_DIR):
        raise HTTPException(status_code=403, detail="Invalid file path")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename,
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )


# 筆記字幕檔
@note_router.get("/srt/{user_id}/{time_stap}", response_class=FileResponse)
async def get_srt_file(user_id: str, time_stap: str):
    filename = "note.zh.srt"
    safe_user_path = os.path.normpath(
        os.path.join(BASE_DIR, user_id, "Note", time_stap)
    )
    file_path = os.path.normpath(os.path.join(safe_user_path, filename))
    print(f"📄 Resolving subtitle path: {file_path}")

    # 安全性檢查：防止路徑穿越
    if os.path.commonpath([BASE_DIR, file_path]) != os.path.abspath(BASE_DIR):
        raise HTTPException(status_code=403, detail="Invalid file path")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Subtitle file not found")

    return FileResponse(
        path=file_path,
        media_type="application/x-subrip",  # 或 "text/plain"
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
