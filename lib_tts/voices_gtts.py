from gtts import gTTS
import os

# 目前語音選擇數很少。


def text_to_speech(
    text: str, lang: str = "en", tld="com.au", filename: str = "c:/temp/output.mp3"
):
    # 建立 gTTS 語音物件
    tts = gTTS(text=text, lang=lang, tld=tld)

    # 儲存為 MP3 檔案
    tts.save(filename)
    print(f"語音已儲存為 {filename}")

    # 自動播放（僅限支援的作業系統）
    try:
        if os.name == "nt":  # Windows
            os.system(f"start {filename}")
        elif os.name == "posix":  # macOS/Linux
            os.system(f"open {filename}")  # macOS 可用 'afplay' 替代
    except Exception as e:
        print(f"播放失敗：{e}")


# 測試
if __name__ == "__main__":
    text = "Hello. This is a example for gtts"
    text_to_speech(text)
