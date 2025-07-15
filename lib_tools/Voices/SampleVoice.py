import asyncio
import edge_tts
from pathlib import Path

# 可自訂輸出目錄
OUTPUT_DIR = Path("c:/temp/0715")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def generate_single_voice(voice: str, label: str, text: str):
    output_path = OUTPUT_DIR / f"{voice}_{label}.mp3"
    tts = edge_tts.Communicate(text, voice=voice)
    await tts.save(str(output_path))
    print(f"\n✅ 語音檔已產生: {output_path.resolve()}")


if __name__ == "__main__":
    try:
        voice = input("請輸入語音 ID（例如 en-US-JennyNeural）：").strip()
        label = input("請輸入語音顯示名稱（例如 Jenny）：").strip()
        print("請輸入語音內容（可多行，輸入空行結束）：")

        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)

        text = "\n".join(lines)
        asyncio.run(generate_single_voice(voice, label, text))

    except KeyboardInterrupt:
        print("\n❗ 中斷執行")
