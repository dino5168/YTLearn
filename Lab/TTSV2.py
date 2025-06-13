import edge_tts
import asyncio
import os


class TTSItem:
    def __init__(self, letter=None, en_text=None, zh_text=None):
        self.letter = letter
        self.en = en_text
        self.zh = zh_text

    def __str__(self):
        return f"Letter: {self.letter} | EN: {self.en} | ZH: {self.zh}"


class TTSReader:
    def __init__(self):
        self.items = []

    def load_from_file(self, filename):
        current = TTSItem()
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue

                key, text = line.split(":", 1)
                key, text = key.strip(), text.strip()

                if key == "letter":
                    if current.letter:  # 有上一筆就先存起來
                        self.items.append(current)
                        current = TTSItem()
                    current.letter = text
                elif key == "en":
                    current.en = text
                elif key == "zh":
                    current.zh = text

        if current.letter:
            self.items.append(current)

    async def generate_tts(self, output_dir="output"):
        os.makedirs(output_dir, exist_ok=True)
        for i, item in enumerate(self.items, start=1):
            index = f"{i:03d}_{item.letter}"
            if item.en:
                tts = edge_tts.Communicate(text=item.en, voice="en-US-AriaNeural")
                await tts.save(os.path.join(output_dir, f"{index}_en.mp3"))

            if item.zh:
                tts = edge_tts.Communicate(text=item.zh, voice="zh-TW-HsiaoChenNeural")
                await tts.save(os.path.join(output_dir, f"{index}_zh.mp3"))


# ---------- 主程式 ----------


async def main():
    reader = TTSReader()
    reader.load_from_file("translations.txt")  # 你的三行格式檔案
    await reader.generate_tts()


if __name__ == "__main__":
    asyncio.run(main())
