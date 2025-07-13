import asyncio
import edge_tts
import os
import json
from pathlib import Path
from pydub import AudioSegment  # pip install pydub ffmpeg

OUTPUT_DIR = "c:/temp/0713"


async def generate_voice_file(text: str, voice: str, index: int, output_dir: Path):
    output_path = output_dir / f"{index:03d}_{voice}.mp3"
    tts = edge_tts.Communicate(text, voice=voice)
    await tts.save(str(output_path))
    print(f"生成語音: {output_path}")
    return output_path


async def generate_dialogue_from_json(json_path: str, output_filename="dialogue.mp3"):
    with open(json_path, "r", encoding="utf-8") as f:
        dialogues = json.load(f)

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    temp_files = []
    for idx, item in enumerate(dialogues):
        voice = item.get("voice")
        text = item.get("text")
        if not voice or not text:
            print(f"⚠️ 跳過不完整項目: {item}")
            continue
        path = await generate_voice_file(text, voice, idx, output_dir)
        temp_files.append(path)

    # 合併 mp3 音檔
    combined = AudioSegment.empty()
    for path in temp_files:
        combined += AudioSegment.from_mp3(path)
        combined += AudioSegment.silent(duration=300)  # 每句話間隔 0.3 秒

    final_output = output_dir / output_filename
    combined.export(final_output, format="mp3")
    print(f"\n✅ 完整對話音檔輸出: {final_output.resolve()}")


if __name__ == "__main__":
    try:
        input_file = input("請輸入對話 JSON 檔路徑: ").strip()
        asyncio.run(generate_dialogue_from_json(input_file))
    except KeyboardInterrupt:
        print("\n中斷執行")
