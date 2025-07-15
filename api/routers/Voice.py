from pathlib import Path
import edge_tts
import os

import shutil
import asyncio

from fastapi import APIRouter, Depends, Query, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime
from app.config import settings

# 資料庫操作
from lib_db.db.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from lib_sql.SQLQueryExecutor import SQLQueryExecutor

from lib_sql.sql_loader_singleton import get_sql_loader
from lib_util.Auth import get_current_user  # Import the dependency


from lib_db.models.User import User
from lib_util.utils import format_user_id

#
from lib_util.StoryVoiceGenerator import StoryVoiceGenerator

UPLOAD_DIR = settings.UPLOAD_DIR
TTS_DIR = settings.TTS_DIR
USERS_DATA_DIR = settings.USERS_DATA_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)

voice_router = APIRouter(
    prefix="/voices",
    tags=["voices"],
)

sql_loader = get_sql_loader()

# 原始資料
En_Voices = {
    "en-AU-NatashaNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-AU-WilliamNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-CA-ClaraNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-CA-LiamNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-GB-LibbyNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-GB-MaisieNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-GB-RyanNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-GB-SoniaNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-GB-ThomasNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-HK-SamNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-HK-YanNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-IE-ConnorNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-IE-EmilyNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-IN-NeerjaExpressiveNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-IN-NeerjaNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-IN-PrabhatNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-KE-AsiliaNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-KE-ChilembaNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-NG-AbeoNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-NG-EzinneNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-NZ-MitchellNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-NZ-MollyNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-PH-JamesNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-PH-RosaNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-SG-LunaNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-SG-WayneNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-TZ-ElimuNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-TZ-ImaniNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-US-AnaNeural": {
        "gender": "Female",
        "style": "Cartoon, Conversation",
        "attributes": ["Cute"],
    },
    "en-US-AndrewMultilingualNeural": {
        "gender": "Male",
        "style": "Conversation, Copilot",
        "attributes": ["Warm", "Confident", "Authentic", "Honest"],
    },
    "en-US-AndrewNeural": {
        "gender": "Male",
        "style": "Conversation, Copilot",
        "attributes": ["Warm", "Confident", "Authentic", "Honest"],
    },
    "en-US-AriaNeural": {
        "gender": "Female",
        "style": "News, Novel",
        "attributes": ["Positive", "Confident"],
    },
    "en-US-AvaMultilingualNeural": {
        "gender": "Female",
        "style": "Conversation, Copilot",
        "attributes": ["Expressive", "Caring", "Pleasant", "Friendly"],
    },
    "en-US-AvaNeural": {
        "gender": "Female",
        "style": "Conversation, Copilot",
        "attributes": ["Expressive", "Caring", "Pleasant", "Friendly"],
    },
    "en-US-BrianMultilingualNeural": {
        "gender": "Male",
        "style": "Conversation, Copilot",
        "attributes": ["Approachable", "Casual", "Sincere"],
    },
    "en-US-BrianNeural": {
        "gender": "Male",
        "style": "Conversation, Copilot",
        "attributes": ["Approachable", "Casual", "Sincere"],
    },
    "en-US-ChristopherNeural": {
        "gender": "Male",
        "style": "News, Novel",
        "attributes": ["Reliable", "Authority"],
    },
    "en-US-EmmaMultilingualNeural": {
        "gender": "Female",
        "style": "Conversation, Copilot",
        "attributes": ["Cheerful", "Clear", "Conversational"],
    },
    "en-US-EmmaNeural": {
        "gender": "Female",
        "style": "Conversation, Copilot",
        "attributes": ["Cheerful", "Clear", "Conversational"],
    },
    "en-US-EricNeural": {
        "gender": "Male",
        "style": "News, Novel",
        "attributes": ["Rational"],
    },
    "en-US-GuyNeural": {
        "gender": "Male",
        "style": "News, Novel",
        "attributes": ["Passion"],
    },
    "en-US-JennyNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Considerate", "Comfort"],
    },
    "en-US-MichelleNeural": {
        "gender": "Female",
        "style": "News, Novel",
        "attributes": ["Friendly", "Pleasant"],
    },
    "en-US-RogerNeural": {
        "gender": "Male",
        "style": "News, Novel",
        "attributes": ["Lively"],
    },
    "en-US-SteffanNeural": {
        "gender": "Male",
        "style": "News, Novel",
        "attributes": ["Rational"],
    },
    "en-ZA-LeahNeural": {
        "gender": "Female",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
    "en-ZA-LukeNeural": {
        "gender": "Male",
        "style": "General",
        "attributes": ["Friendly", "Positive"],
    },
}

# 確保 uploads 目錄存在
# UPLOAD_DIR = "c:/temp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class TTSRequest(BaseModel):
    voice_id: str
    text: str


@voice_router.get("/enlist")
def list_voices(
    gender: Optional[str] = Query(None, description="性別：Male 或 Female"),
    style: Optional[str] = Query(None, description="語音風格，如 General, News"),
    attribute: Optional[str] = Query(None, description="語音屬性，如 Friendly, Clear"),
):
    """
    取得語音清單，可選擇篩選條件（性別、風格、屬性）
    """
    results = []

    for voice_id, meta in En_Voices.items():
        if gender and meta["gender"].lower() != gender.lower():
            continue
        if style and style.lower() not in meta["style"].lower():
            continue
        if attribute and all(
            attribute.lower() not in a.lower() for a in meta["attributes"]
        ):
            continue

        results.append(
            {
                "voice_id": voice_id,
                "gender": meta["gender"],
                "style": meta["style"],
                "attributes": meta["attributes"],
            }
        )

    return {"count": len(results), "voices": results}


## 語音合成
@voice_router.post("/tts")
async def generate_tts(
    data: TTSRequest, current_user: User = Depends(get_current_user)
):
    id = current_user["id"]
    formatId = format_user_id(id)
    current_user_path = os.path.join(USERS_DATA_DIR, formatId, "Note")
    current_user_path = Path(current_user_path)  # <-- 加這行，如果原本是 str
    voice = data.voice_id
    text = data.text.strip()
    print(f"Current User: {current_user["email"]}")  # 確認使用者已登入
    print(f"Voice ID: {voice}")  # 語音 ID
    print(text)

    if not text:
        return JSONResponse(content={"error": "text is empty"}, status_code=400)

    try:
        # 建立 output 資料夾（如果還沒建立）

        os.makedirs(current_user_path, exist_ok=True)
        # 建立唯一目錄
        print("建立唯一檔名")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.mp3"
        print(filename)
        output_filename = os.path.join(current_user_path, filename)

        # 使用 edge-tts 進行語音合成
        print("execute - tts")
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(output_filename)
        # test 產出資料

        notePath = os.path.join(current_user_path, timestamp)

        os.makedirs(notePath, exist_ok=True)
        notePath = Path(notePath)
        print(notePath)
        print(voice)

        # generator = StoryVoiceGenerator(voice, notePath)
        generator = StoryVoiceGenerator(voice=voice, output_dir=notePath)
        story_text = text
        print("story_text=================")
        print(story_text)
        await generator.generate_story_from_text(story_text)  # ✅ 正確用 await

        return {
            "status": "success",
            "message": "語音合成完成",
            "file": filename,
            "path": output_filename,
        }

    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


# # 語音錄製上傳
@voice_router.post("/recorder")
async def upload_voice(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    print("==================recorder=================")

    try:
        # 使用 10 碼的 ID 當目錄
        id = current_user["id"]
        formatId = format_user_id(id)
        current_user_path = os.path.join(USERS_DATA_DIR, formatId, "Recorder")

        # save_user_path = os.path.join(
        #    current_user_path, f"{current_user["id"]}_{current_user["name"]}"
        # )

        os.makedirs(current_user_path, exist_ok=True)

        ext = os.path.splitext(file.filename)[1] or ".webm"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(current_user_path, f"{timestamp}{ext}")

        executor = SQLQueryExecutor(sql_loader, db)
        sql_key = "INSERT_USER_UPLOAD_RECORDER"
        params = {"user_id": id, "file_name": save_path, "file_path": current_user_path}
        print(params)
        result = await executor.execute(sql_key, params)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return JSONResponse(content={"message": "Upload successful", "file": save_path})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": str(e)})
