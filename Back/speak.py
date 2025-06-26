import asyncio
from bs4 import BeautifulSoup
import edge_tts

# Step 1: 讀取 HTML 並擷取純文字
with open("c:/ai/html/a02.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")
    text = soup.get_text()


# Step 2: edge-tts 將文字轉語音 MP3
async def save_mp3(text):
    voice = "zh-TW-HsiaoChenNeural"  # 台灣女生自然語音
    output_file = "c:/ai/html/output.mp3"
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(output_file)
    print(f"語音已儲存為 {output_file}")


# 執行
asyncio.run(save_mp3(text))
