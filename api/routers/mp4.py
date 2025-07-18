from pathlib import Path
from fastapi import APIRouter, FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi import Request
from app.config import settings

# 資料庫操作
from lib_db.db.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from lib_sql.SQLQueryExecutor import SQLQueryExecutor

from lib_sql.sql_loader_singleton import get_sql_loader
from lib_util.Auth import get_current_user  # Import the dependency
from lib_db.models.User import User
from lib_util.utils import format_user_id

import json
import os
import shutil
from datetime import datetime
import uuid
import logging


# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


mp4_router = APIRouter(prefix="/mp4", tags=["mp4"])


# 資料模型
class VoiceDataItem(BaseModel):
    id: int
    text: str
    selectedValue: Optional[str] = None
    selectedLabel: Optional[str] = None
    hasImage: bool = False
    imageName: Optional[str] = None


class VoiceDataResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None


# 設定檔案儲存路徑
MP4_UPLOAD_DIR = os.path.join(settings.USERS_DATA_DIR, "MP4")

DATA_DIR = os.path.join(MP4_UPLOAD_DIR, "data")

# 創建必要的目錄

os.makedirs(DATA_DIR, exist_ok=True)


# 儲存上傳的 Image 檔案
def save_uploaded_file(file: UploadFile, destination: str) -> str:
    """儲存上傳的檔案"""
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return destination
    except Exception as e:
        logger.error(f"檔案儲存失敗: {e}")
        raise HTTPException(status_code=500, detail=f"檔案儲存失敗: {str(e)}")


def validate_image_file(file: UploadFile) -> bool:
    """驗證圖片檔案"""
    # 檢查檔案類型
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        return False

    # 檢查檔案大小 (5MB 限制)
    if file.size and file.size > 5 * 1024 * 1024:
        return False

    return True


from starlette.datastructures import UploadFile as StarletteUploadFile


@mp4_router.post("/voice-data", response_model=VoiceDataResponse)
async def receive_voice_data(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    接收語音資料和圖片檔案
    """

    # 假設 current_user 是字典，含有 user 的 ID
    user_id = current_user["id"]

    # 格式化 user_id，例如補零變成 '000123'
    formatId = format_user_id(user_id)

    # 建立使用者專屬目錄路徑
    current_user_path = Path(MP4_UPLOAD_DIR) / formatId

    # 加入 timestamp 子資料夾
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_user_path = current_user_path / timestamp  # Path 物件可直接使用 /

    # 印出即將建立的路徑
    print(current_user_path)

    # 建立資料夾（包含父層目錄）
    os.makedirs(current_user_path, exist_ok=True)

    form = await request.form()
    print("=============form==============")
    print(form)
    # user.role_id

    # 取得 JSON payload
    data = form.get("data")
    if not data:
        raise HTTPException(status_code=400, detail="缺少 data 欄位")

    try:
        voice_data_list = json.loads(data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON 格式錯誤: {str(e)}")

    # 驗證格式
    validated_data = []
    for item in voice_data_list:
        try:
            validated_item = VoiceDataItem(**item)
            validated_data.append(validated_item)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"資料格式錯誤: {str(e)}")

    # 儲存圖片
    print("儲存圖片")
    saved_files = {}
    for key in form.keys():
        if key == "data":
            continue
        upload_file = form.get(key)
        print(type(upload_file))  # 看看到底是什麼型態

        print(upload_file)
        if isinstance(upload_file, StarletteUploadFile):
            if not validate_image_file(upload_file):
                print("❌ validate_image_file 回傳 False")
                print(f"upload_file.filename = {upload_file.filename}")
                print(f"upload_file.content_type = {upload_file.content_type}")
                print(f"upload_file.size = {upload_file.size}")
                raise HTTPException(
                    status_code=400,
                    detail=f"檔案 {upload_file.filename} 格式不正確或檔案過大",
                )

            file_extension = os.path.splitext(upload_file.filename)[1]
            print(file_extension)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            new_filename = f"{timestamp}_{unique_id}{file_extension}"

            file_path = os.path.join(current_user_path, new_filename)
            print(file_path)
            save_uploaded_file(upload_file, file_path)

            saved_files[key] = {
                "original_name": upload_file.filename,
                "saved_name": new_filename,
                "file_path": file_path,
                "file_size": upload_file.size,
            }
        else:
            print("if this line here display then have errors")

    # 更新 JSON 的 imageName
    for item in validated_data:
        if item.hasImage and item.imageName in saved_files:
            item.imageName = saved_files[item.imageName]["saved_name"]

    # 儲存 JSON : 文字檔
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"{timestamp}.json"
    with open(
        os.path.join(current_user_path, json_filename), "w", encoding="utf-8"
    ) as f:
        json.dump(
            [item.dict() for item in validated_data], f, ensure_ascii=False, indent=2
        )

    # 資料上傳成功 新增資料到資料庫

    return VoiceDataResponse(
        success=True,
        message="資料接收成功",
        data={
            "processed_items": len(validated_data),
            "saved_images": len(saved_files),
            "json_file": json_filename,
            "image_files": list(saved_files.values()),
        },
    )


@mp4_router.get("/voice-data", response_model=VoiceDataResponse)
async def get_voice_data_list():
    """
    取得已儲存的語音資料列表
    """
    try:
        data_files = []
        if os.path.exists(DATA_DIR):
            for filename in os.listdir(DATA_DIR):
                if filename.endswith(".json"):
                    file_path = os.path.join(DATA_DIR, filename)
                    file_stat = os.stat(file_path)
                    data_files.append(
                        {
                            "filename": filename,
                            "created_time": datetime.fromtimestamp(
                                file_stat.st_ctime
                            ).isoformat(),
                            "size": file_stat.st_size,
                        }
                    )

        return VoiceDataResponse(
            success=True, message="取得資料列表成功", data={"files": data_files}
        )

    except Exception as e:
        logger.error(f"取得資料列表時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"伺服器內部錯誤: {str(e)}")


@mp4_router.get("/voice-data/{filename}")
async def get_voice_data_file(filename: str):
    """
    取得特定的語音資料檔案內容
    """
    try:
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path) or not filename.endswith(".json"):
            raise HTTPException(status_code=404, detail="檔案不存在")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return VoiceDataResponse(
            success=True, message="取得檔案成功", data={"content": data}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得檔案時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"伺服器內部錯誤: {str(e)}")


@mp4_router.get("/")
async def root():
    """
    API 根路徑
    """
    return {
        "message": "語音資料接收 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/voice-data": "接收語音資料和圖片",
            "GET /api/voice-data": "取得資料列表",
            "GET /api/voice-data/{filename}": "取得特定檔案",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mp4_router, host="0.0.0.0", port=8000)
