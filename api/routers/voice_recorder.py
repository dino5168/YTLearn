from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime


voice_recorder_router = APIRouter(
    prefix="/voices",
    tags=["voices"],
)

# 確保 uploads 目錄存在
# 讀取設定檔
from app.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


@voice_recorder_router.post("/recorder")
async def upload_voice(file: UploadFile = File(...)):
    try:
        print("Received file:")
        ext = os.path.splitext(file.filename)[1] or ".webm"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(UPLOAD_DIR, f"recording_{timestamp}{ext}")
        print(f"Saving file to: {save_path}")

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return JSONResponse(content={"message": "Upload successful", "file": save_path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
