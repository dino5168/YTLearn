import edge_tts
import os
import uuid
import shutil

from fastapi import APIRouter, Query, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime


voice_router = APIRouter(
    prefix="/voices",
    tags=["voices"],
)

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
UPLOAD_DIR = "c:/temp/uploads"
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


@voice_router.post("/tts")
async def generate_tts(data: TTSRequest):
    voice = data.voice_id
    text = data.text.strip()

    if not text:
        return JSONResponse(content={"error": "text is empty"}, status_code=400)

    try:
        # 建立 output 資料夾（如果還沒建立）
        output_dir = "c:/temp/output_audio"
        os.makedirs(output_dir, exist_ok=True)

        # 建立唯一檔名
        filename = f"{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(output_dir, filename)

        # 使用 edge-tts 進行語音合成
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(output_path)

        return {
            "status": "success",
            "message": "語音合成完成",
            "file": filename,
            "path": output_path,
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@voice_router.post("/recorder")
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
