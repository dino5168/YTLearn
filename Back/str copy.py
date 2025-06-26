import whisper


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


# 載入模型
model = whisper.load_model("base")  # 也可以換成 tiny, small, medium, large

# 轉錄音訊檔案
result = model.transcribe("C://Mp3//test/01.mp3")

# 將轉錄結果輸出為 SRT 字幕檔
write_srt(result["segments"], "C://Mp3//test/01.srt")

print("轉錄完成，字幕檔已產生。")
