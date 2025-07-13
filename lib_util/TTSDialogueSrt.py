import asyncio
import edge_tts
import os
import json
from pathlib import Path
from pydub import AudioSegment  # pip install pydub ffmpeg

OUTPUT_DIR = "c:/temp/0713"
SILENCE_DURATION = 300  # 毫秒


def format_timestamp(ms: int) -> str:
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


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
    text_segments = []

    for idx, item in enumerate(dialogues):
        voice = item.get("voice")
        text = item.get("text")
        if not voice or not text:
            print(f"⚠️ 跳過不完整項目: {item}")
            continue
        path = await generate_voice_file(text, voice, idx, output_dir)
        temp_files.append(path)
        text_segments.append(text)

    # 合併 mp3 與字幕
    combined = AudioSegment.empty()
    srt_entries = []
    current_time = 0

    for idx, (path, text) in enumerate(zip(temp_files, text_segments)):
        segment = AudioSegment.from_mp3(path)
        start_time = current_time
        end_time = current_time + len(segment)

        # 建立 SRT 條目
        srt_entry = f"{idx + 1}\n{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n{text}\n"
        srt_entries.append(srt_entry)

        combined += segment
        combined += AudioSegment.silent(duration=SILENCE_DURATION)
        current_time = end_time + SILENCE_DURATION

    # 輸出 mp3
    final_mp3 = output_dir / output_filename
    combined.export(final_mp3, format="mp3")
    print(f"\n✅ 完整對話音檔輸出: {final_mp3.resolve()}")

    # 輸出 srt
    srt_path = final_mp3.with_suffix(".srt")
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write("\n".join(srt_entries))
    print(f"✅ 字幕檔輸出: {srt_path.resolve()}")


if __name__ == "__main__":
    try:
        input_file = input("請輸入對話 JSON 檔路徑: ").strip()
        asyncio.run(generate_dialogue_from_json(input_file))
    except KeyboardInterrupt:
        print("\n中斷執行")
