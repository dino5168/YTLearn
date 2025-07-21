from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile
import shutil
import os
import uuid
from faster_whisper import WhisperModel


class FasterWhisperTranscriber:
    def __init__(
        self, model_name="small", output_dir=None, device="auto", compute_type="auto"
    ):
        """
        初始化 FasterWhisper 轉錄器

        Args:
            model_name: 模型大小 (tiny, base, small, medium, large, large-v2, large-v3)
            output_dir: 輸出目錄
            device: 設備 ("cpu", "cuda", "auto")
            compute_type: 計算類型 ("int8", "int16", "float16", "float32", "auto")
        """
        print(f"[FasterWhisper] 載入模型：{model_name} ...")
        print(f"[FasterWhisper] 設備：{device}, 計算類型：{compute_type}")

        try:
            # 載入模型
            self.model = WhisperModel(
                model_name, device=device, compute_type=compute_type
            )
            print("[FasterWhisper] ✓ 模型載入完成")
        except Exception as e:
            print(f"[FasterWhisper] ✗ 模型載入失敗: {e}")
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

        # 支援的檔案副檔名
        self.allowed_extensions = {
            ".mp3",
            ".wav",
            ".m4a",
            ".flac",
            ".ogg",
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".webm",
        }

    def _format_timestamp(self, seconds: float) -> str:
        """格式化時間戳記為 SRT 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _write_srt(self, segments, file_path: Path):
        """寫入 SRT 字幕檔"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segments, 1):
                    start = self._format_timestamp(segment.start)
                    end = self._format_timestamp(segment.end)
                    text = segment.text.strip()
                    f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        except Exception as e:
            raise Exception(f"SRT 檔案寫入失敗: {str(e)}")

    def _validate_local_file(self, file_path: str):
        """驗證本地檔案"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"找不到檔案: {file_path}")

        file_size = path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(
                f"檔案過大，最大允許 {self.max_file_size // (1024*1024)}MB"
            )

        if path.suffix.lower() not in self.allowed_extensions:
            raise ValueError(f"不支援的檔案格式: {path.suffix}")

    def transcribe_from_file(self, file_path: str, language="en", **kwargs) -> dict:
        """
        從本地檔案轉錄音訊

        Args:
            file_path: 檔案路徑
            language: 語言代碼 (en, zh, ja, ko 等)
            **kwargs: 其他參數 (beam_size, best_of, temperature 等)
        """
        self._validate_local_file(file_path)

        file_path = Path(file_path)

        try:
            print(f"[FasterWhisper] 開始轉錄檔案: {file_path.name}")
            print(f"[FasterWhisper] 語言: {language}")

            # 使用 faster-whisper 轉錄
            segments, info = self.model.transcribe(
                str(file_path),
                language=language,
                beam_size=kwargs.get("beam_size", 5),
                best_of=kwargs.get("best_of", 5),
                temperature=kwargs.get("temperature", 0),
                condition_on_previous_text=kwargs.get(
                    "condition_on_previous_text", True
                ),
                vad_filter=kwargs.get("vad_filter", True),  # 語音活動檢測
                vad_parameters=kwargs.get("vad_parameters", None),
            )

            # 轉換 segments 為 list
            segments_list = []
            for segment in segments:
                segments_list.append(
                    {"start": segment.start, "end": segment.end, "text": segment.text}
                )

            print(f"[FasterWhisper] ✓ 轉錄完成")
            print(
                f"[FasterWhisper] 偵測到的語言: {info.language} (信心度: {info.language_probability:.2f})"
            )
            print(f"[FasterWhisper] 總時長: {info.duration:.2f} 秒")

        except Exception as e:
            raise Exception(f"轉錄失敗: {str(e)}")

        # 建立輸出檔案
        try:
            srt_filename = f"{file_path.stem}.srt"
            srt_path = self.output_dir / srt_filename

            # 重新轉換為 segments 物件以寫入 SRT
            class SegmentObj:
                def __init__(self, start, end, text):
                    self.start = start
                    self.end = end
                    self.text = text

            segment_objs = [
                SegmentObj(s["start"], s["end"], s["text"]) for s in segments_list
            ]
            self._write_srt(segment_objs, srt_path)

        except Exception as e:
            raise Exception(f"SRT 檔案建立失敗: {str(e)}")

        return {
            "message": f"{language.upper()} 轉錄成功",
            "language": language,
            "detected_language": info.language,
            "language_probability": info.language_probability,
            "segments": segments_list,
            "srt_file": str(srt_path),
            "total_duration": info.duration,
            "vad_enabled": kwargs.get("vad_filter", True),
        }

    def _validate_upload_file(self, file: UploadFile):
        """驗證上傳檔案"""
        if hasattr(file, "size") and file.size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"檔案過大，最大允許 {self.max_file_size // (1024*1024)}MB",
            )

        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400, detail=f"不支援的檔案格式: {file.content_type}"
            )

    def transcribe_from_upload(self, file: UploadFile, language="en", **kwargs) -> dict:
        """從 FastAPI UploadFile 轉錄音訊"""
        self._validate_upload_file(file)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_extension = Path(file.filename).suffix if file.filename else ".tmp"
            temp_audio_path = os.path.join(
                tmpdir, f"audio_{uuid.uuid4().hex}{file_extension}"
            )

            try:
                # 儲存上傳的檔案
                with open(temp_audio_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

                # 轉錄
                result = self.transcribe_from_file(temp_audio_path, language, **kwargs)

                # 更新檔案名稱
                if file.filename:
                    original_name = Path(file.filename).stem
                    srt_filename = f"{original_name}.srt"
                    new_srt_path = self.output_dir / srt_filename

                    # 重新命名 SRT 檔案
                    Path(result["srt_file"]).rename(new_srt_path)
                    result["srt_file"] = str(new_srt_path)

                return result

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"轉錄失敗: {str(e)}")


# 使用範例
if __name__ == "__main__":
    # 方法1: 自動選擇最佳設定
    transcriber = FasterWhisperTranscriber(
        model_name="small",
        output_dir="c:/temp/output_srt",
        device="cpu",  # 自動選擇 CPU 或 GPU
        compute_type="int8",  # 自動選擇計算精度
    )

    # 方法2: 手動指定 GPU 設定 (如果你有 NVIDIA GPU)
    # transcriber = FasterWhisperTranscriber(
    #     model_name="small",
    #     output_dir="c:/temp/output_srt",
    #     device="cuda",
    #     compute_type="float16"  # GPU 上使用 FP16
    # )

    # 方法3: 手動指定 CPU 設定
    # transcriber = FasterWhisperTranscriber(
    #     model_name="small",
    #     output_dir="c:/temp/output_srt",
    #     device="cpu",
    #     compute_type="int8"  # CPU 上使用 8-bit 量化
    # )

    mp3file = r"C:\temp\1.mp3"

    try:
        result = transcriber.transcribe_from_file(
            mp3file,
            language="en",
            beam_size=5,  # 束搜尋大小 (1-10，越大越準但越慢)
            temperature=0,  # 溫度參數 (0 = 確定性輸出)
            vad_filter=True,  # 語音活動檢測 (過濾靜音)
            condition_on_previous_text=True,  # 基於前文預測
        )

        print("✅ 轉錄完成")
        print("字幕儲存於：", result["srt_file"])
        print("總時長：", f"{result['total_duration']:.2f} 秒")
        print("偵測到的語言：", result["detected_language"])
        print("語言信心度：", f"{result['language_probability']:.2f}")
        print("片段數量：", len(result["segments"]))

        # 顯示前5段字幕
        print("\n前5段字幕內容：")
        for i, segment in enumerate(result["segments"][:5], 1):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"].strip()
            print(f"{i}. [{start_time:.1f}s - {end_time:.1f}s] {text}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
