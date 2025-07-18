import asyncio
import json
import os
from pathlib import Path
from StoryVoiceGenerator import StoryVoiceGenerator

from TransSrt import translate_and_merge_srt

import re
from datetime import timedelta


def parse_srt_time_to_seconds(time_str: str) -> float:
    """將 SRT 時間字串轉為秒數"""
    h, m, s_ms = time_str.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def format_seconds_to_srt_time(seconds: float) -> str:
    """將秒數轉為 SRT 時間格式"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    ms = int((seconds - total_seconds) * 1000)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


async def fix_srt_timings_continuous(input_path: str, output_path: str = None):
    """
    調整 SRT 檔案的時間軸為連續不中斷的版本
    會保持原本每段字幕的長度，但讓每段字幕緊接著上一段結束後顯示
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())
    subtitles = []

    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 3:
            index = lines[0]
            times = lines[1]
            text = lines[2:]
            start_str, end_str = times.split("-->")
            start = parse_srt_time_to_seconds(start_str.strip())
            end = parse_srt_time_to_seconds(end_str.strip())
            subtitles.append({"index": index, "duration": end - start, "text": text})

    # 重新安排時間軸
    new_blocks = []
    current_time = 0.0

    for i, sub in enumerate(subtitles, start=1):
        start = current_time
        end = start + sub["duration"]
        start_str = format_seconds_to_srt_time(start)
        end_str = format_seconds_to_srt_time(end)
        block = [str(i), f"{start_str} --> {end_str}", *sub["text"]]
        new_blocks.append("\n".join(block))
        current_time = end  # 下一段從這段結束開始

    result_srt = "\n\n".join(new_blocks)

    if not output_path:
        output_path = input_path.replace(".srt", ".time.srt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_srt)

    print(f"✔️ 已成功輸出連續字幕時間軸到: {output_path}")


async def generate_from_json_per_id_with_sentences(
    json_path: str,
    output_dir: str = "c:/temp/0718",
    default_voice: str = "en-US-JennyNeural",
):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in data:
        text = item.get("text", "").strip()
        if not text:
            continue

        voice = item.get("selectedValue") or default_voice
        id_str = str(item["id"])
        output_srt = f"{id_str}.srt"
        output_mp3 = f"{id_str}.mp3"

        # 每筆建立獨立語音產生器
        generator = StoryVoiceGenerator(
            voice=voice,
            output_dir=output_dir,
            output_mp3=output_mp3,
            output_srt=output_srt,
            silence_ms=300,
        )

        en_source_srt = os.path.join(output_dir, output_srt)

        # 呼叫完整多句切割邏輯
        await generator.generate_story_from_text(content=text)
        # 調整時間軸
        await fix_srt_timings_continuous(en_source_srt, en_source_srt)

        # 翻譯

        zhtw_srt = os.path.join(output_dir, f"{id_str}.zhtw.srt")
        print(en_source_srt, zhtw_srt)
        translate_and_merge_srt(en_source_srt, zhtw_srt)

        print(f"✅ 已完成：{id_str}.mp3 / {id_str}.srt")


# ✅ 執行
if __name__ == "__main__":
    json_file = (
        r"C:\ytdb\users_data\MP4\0000000029\20250718_062951\20250718_062951.json"
    )
    asyncio.run(generate_from_json_per_id_with_sentences(json_file))
