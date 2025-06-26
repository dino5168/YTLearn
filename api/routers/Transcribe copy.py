from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile
import shutil
import os
import whisper

transcribe_router = APIRouter()
model_name = "medium"
print(f"[Whisper] 載入模型：{model_name} ...")
model = whisper.load_model(model_name)
print("[Whisper] ✓ 模型載入完成")


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, 1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


@transcribe_router.post("/transcribe", tags=["Whisper"])
async def transcribe_audio(file: UploadFile = File(...), language: str = Form("en")):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, file.filename)
            with open(audio_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            # 語音辨識
            result = model.transcribe(audio_path, language=language)

            # 寫入 SRT（選擇性）
            srt_path = Path(audio_path).with_suffix(".srt")
            write_srt(result["segments"], srt_path)

            return {
                "message": "轉錄成功",
                "language_detected": result.get("language", language),
                "segments": result["segments"],
                "srt_file": srt_path.name,  # 可改為提供下載連結
            }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
