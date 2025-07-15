import asyncio
import edge_tts
import os
import re
from pathlib import Path
from pydub import AudioSegment

VOICE = "en-US-JennyNeural"
OUTPUT_DIR = Path("c:/temp/0713")
OUTPUT_MP3 = OUTPUT_DIR / "story.mp3"
OUTPUT_SRT = OUTPUT_DIR / "story.srt"
SILENCE_MS = 300


def split_text_into_sentences(text: str):
    # 根據標點符號切割，保留句尾
    pattern = r"(?<=[.!?])\s+"
    sentences = re.split(pattern, text.strip())
    return [s.strip() for s in sentences if s.strip()]


def format_timestamp(ms: int) -> str:
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


async def generate_voice_file(
    text: str, voice: str, index: int, output_dir: Path
) -> Path:
    output_path = output_dir / f"{index:03d}.mp3"
    tts = edge_tts.Communicate(text, voice=voice)
    await tts.save(str(output_path))
    print(f"✔️ 產生語音: {output_path.name}")
    return output_path


async def generate_story_from_text_file(text_file: str):
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 讀取文字
    with open(text_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 切割句子
    sentences = split_text_into_sentences(content)
    print(f"📖 共 {len(sentences)} 句話")

    temp_files = []
    for idx, sentence in enumerate(sentences):
        path = await generate_voice_file(sentence, VOICE, idx + 1, OUTPUT_DIR)
        temp_files.append((path, sentence))

    # 合併 mp3，建立 srt
    combined = AudioSegment.empty()
    srt_entries = []
    current_time = 0

    for idx, (path, text) in enumerate(temp_files):
        segment = AudioSegment.from_mp3(path)
        start = current_time
        end = current_time + len(segment)

        srt_entry = f"{idx + 1}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{text}\n"
        srt_entries.append(srt_entry)

        combined += segment
        combined += AudioSegment.silent(duration=SILENCE_MS)
        current_time = end + SILENCE_MS

    # 輸出 mp3
    combined.export(OUTPUT_MP3, format="mp3")
    print(f"\n✅ 合併音檔輸出: {OUTPUT_MP3.resolve()}")

    # 輸出 srt
    with open(OUTPUT_SRT, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    print(f"✅ 字幕檔輸出: {OUTPUT_SRT.resolve()}")


if __name__ == "__main__":
    try:
        input_path = input("請輸入故事文字檔路徑：").strip()
        asyncio.run(generate_story_from_text_file(input_path))
    except KeyboardInterrupt:
        print("\n❗ 中斷執行")
