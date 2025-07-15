import asyncio
import edge_tts
import os


# 將文字轉換成 mp3
async def text_to_speech(text: str, voice: str, output_file: str = "output.mp3"):
    """
    使用 edge-tts 將文字轉語音並輸出 mp3

    :param text: 要轉換的文字內容
    :param voice: 語音名稱，例如 'zh-TW-HsiaoChenNeural'
    :param output_file: 輸出 mp3 檔案名稱，預設為 output.mp3
    """
    if not text.strip():
        print("❌ 輸入文字為空")
        return

    if not output_file.endswith(".mp3"):
        output_file += ".mp3"

    print(f"\n🗣️ 開始語音轉換...")
    print(f"🔤 文字長度: {len(text)} 字元")
    print(f"🧑‍🎤 使用語音: {voice}")
    print(f"💾 輸出檔案: {output_file}")

    try:
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(output_file)

        file_size = os.path.getsize(output_file)
        print(f"\n✅ 轉換完成！")
        print(f"📁 檔案位置: {os.path.abspath(output_file)}")
        print(f"📦 檔案大小: {file_size:,} bytes")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")


# 呼叫範例（在其他程式中使用）
if __name__ == "__main__":
    # 測試用：直接執行產生語音
    sample_text = "你好，這是一段語音合成的示範文字。"
    sample_voice = "zh-TW-HsiaoChenNeural"
    asyncio.run(text_to_speech(sample_text, sample_voice, "demo_output.mp3"))
