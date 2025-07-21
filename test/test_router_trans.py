from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile
import shutil
import os
import uuid
import whisper


# Whisper Transcription Handler Class
class WhisperTranscriber:
    def __init__(self, model_name="medium", output_dir=None):
        print(f"[Whisper] 載入模型：{model_name} ...")
        try:
            self.model = whisper.load_model(model_name)
            print("[Whisper] ✓ 模型載入完成")
        except Exception as e:
            print(f"[Whisper] ✗ 模型載入失敗: {e}")
            raise

        if output_dir is None:
            output_dir = Path.home() / "temp" / "output_srt"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 檔案大小限制 (100MB)
        self.max_file_size = 100 * 1024 * 1024

        # 支援的檔案格式
        self.allowed_types = {
            "audio/mpeg",
            "audio/wav",
            "audio/mp3",
            "audio/m4a",
            "audio/flac",
            "audio/ogg",
            "video/mp4",
            "video/avi",
        }

    def _format_timestamp(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _write_srt(self, segments, file_path: Path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segments, 1):
                    start = self._format_timestamp(segment["start"])
                    end = self._format_timestamp(segment["end"])
                    text = segment["text"].strip()
                    f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"SRT 檔案寫入失敗: {str(e)}")

    def _validate_file(self, file: UploadFile):
        # 檢查檔案大小
        if hasattr(file, "size") and file.size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"檔案過大，最大允許 {self.max_file_size // (1024*1024)}MB",
            )

        # 檢查檔案類型
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400, detail=f"不支援的檔案格式: {file.content_type}"
            )

    def transcribe(self, file: UploadFile) -> dict:
        # 檔案驗證
        self._validate_file(file)

        # 只允許英文
        language = "en"

        with tempfile.TemporaryDirectory() as tmpdir:
            # 使用安全的檔案名
            file_extension = Path(file.filename).suffix if file.filename else ".tmp"
            temp_audio_path = os.path.join(
                tmpdir, f"audio_{uuid.uuid4().hex}{file_extension}"
            )

            try:
                # 儲存上傳的檔案
                with open(temp_audio_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

                # 語音辨識
                print(f"[Whisper] 開始轉錄檔案: {file.filename}")
                result = self.model.transcribe(temp_audio_path, language=language)
                print(f"[Whisper] ✓ 轉錄完成")

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"轉錄失敗: {str(e)}")

        # 建立輸出檔案
        try:
            original_name = (
                Path(file.filename).stem if file.filename else "transcription"
            )
            srt_filename = f"{original_name}.srt"
            srt_path = self.output_dir / srt_filename
            self._write_srt(result["segments"], srt_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"SRT 檔案建立失敗: {str(e)}")

        return {
            "message": "英文轉錄成功",
            "language": language,
            "segments": result["segments"],
            "srt_file": str(srt_path),
            "total_duration": result.get("duration", 0),
            "detected_language": result.get("language", "unknown"),
        }


# 使用範例
def create_whisper_router():
    router = APIRouter()
    transcriber = WhisperTranscriber()

    @router.post("/transcribe")
    async def transcribe_audio(file: UploadFile = File(...)):
        try:
            result = transcriber.transcribe(file)
            return JSONResponse(content=result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

    return router
