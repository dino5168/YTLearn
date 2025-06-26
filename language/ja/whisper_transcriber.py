from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile
import shutil
import os
import whisper


# Whisper Transcription Handler Class
class WhisperTranscriber:
    def __init__(self, model_name="medium", output_dir="c:/temp/output_srt"):
        print(f"[Whisper] 載入模型：{model_name} ...")
        self.model = whisper.load_model(model_name)
        print("[Whisper] ✓ 模型載入完成")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _format_timestamp(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _write_srt(self, segments, file_path: Path):
        with open(file_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    def transcribe(self, file: UploadFile) -> dict:
        # 只允許日文
        language = "ja"

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_audio_path = os.path.join(tmpdir, file.filename)
            with open(temp_audio_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            # 語音辨識
            result = self.model.transcribe(temp_audio_path, language=language)

        # 建立輸出檔案
        srt_filename = f"{Path(file.filename).stem}.srt"
        srt_path = self.output_dir / srt_filename
        self._write_srt(result["segments"], srt_path)

        return {
            "message": "日語轉錄成功",
            "language": language,
            "segments": result["segments"],
            "srt_file": str(srt_path),
        }


# 建立路由
# transcribe_router = APIRouter()
# whisper_transcriber = WhisperTranscriber(model_name="medium")

"""
@transcribe_router.post("/transcribe", tags=["Whisper"])
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="請上傳音訊檔案")

        result = whisper_transcriber.transcribe(file)
        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
"""
