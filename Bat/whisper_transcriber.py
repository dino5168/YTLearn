import whisper
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments, file_path):
    try:
        output_dir = Path(file_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        return True
    except Exception as e:
        print(f"寫入 SRT 發生錯誤：{e}")
        return False


def transcribe_to_srt(
    audio_path: str,
    output_path: str = None,
    model_name: str = "base",
    language: str = "zh",
) -> bool:
    """
    將音訊轉錄為字幕（SRT），並儲存至指定檔案。
    參數:
        audio_path: 音訊檔案路徑
        output_path: 輸出 SRT 路徑（可選）
        model_name: Whisper 模型名稱（tiny/base/small/medium/large）
        language: 指定語言代碼（例如 "zh", "en"）
    回傳:
        成功為 True，失敗為 False
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        print(f"✗ 檔案不存在：{audio_path}")
        return False

    if output_path is None:
        output_path = str(audio_path.with_suffix(".srt"))

    try:
        model = whisper.load_model(model_name)
    except Exception as e:
        print(f"載入模型失敗：{e}")
        return False

    try:
        result = model.transcribe(str(audio_path), language=language)
    except Exception as e:
        print(f"轉錄失敗：{e}")
        return False

    success = write_srt(result["segments"], output_path)
    if success:
        print(f"✓ 字幕已儲存：{output_path}")
        print(f"  - 偵測語言：{result.get('language', '未知')}")
        print(f"  - 音訊長度：{format_timestamp(result.get('duration', 0))}")
    return success
