from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime


voice_recorder_router = APIRouter(
    prefix="/voices",
    tags=["Subtitles"],
)

# 確保 uploads 目錄存在
UPLOAD_DIR = "c:/temp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@voice_recorder_router.post("/recorder")
async def upload_voice(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1] or ".webm"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(UPLOAD_DIR, f"recording_{timestamp}{ext}")

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return JSONResponse(content={"message": "Upload successful", "file": save_path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
