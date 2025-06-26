import sys
from pathlib import Path
from whisper_transcriber import WhisperTranscriber  # 自訂類別


class MockUploadFile:
    """模擬 FastAPI 的 UploadFile 給 WhisperTranscriber 用"""

    def __init__(self, filepath: Path):
        self.filename = filepath.name
        self.file = open(filepath, "rb")
        self.content_type = "audio/mpeg"

    def close(self):
        self.file.close()


def interactive_mode():
    print("🎤 Whisper 日文語音轉 SRT 工具")
    print("請輸入 MP3/WAV 檔案路徑，或輸入 'exit' 離開")

    transcriber = WhisperTranscriber(model_name="large")

    while True:
        user_input = input("\n📂 請輸入音訊檔案路徑：").strip()

        if user_input.lower() == "exit":
            print("👋 已離開。")
            break

        filepath = Path(user_input)
        if not filepath.exists():
            print(f"❌ 檔案不存在：{filepath}")
            continue

        mock_file = MockUploadFile(filepath)
        try:
            result = transcriber.transcribe(mock_file)
            print("✅ 轉錄完成！")
            print(f"📄 字幕檔案儲存於：{result['srt_file']}")
        except Exception as e:
            print(f"⚠️ 發生錯誤：{e}")
        finally:
            mock_file.close()


if __name__ == "__main__":
    interactive_mode()
