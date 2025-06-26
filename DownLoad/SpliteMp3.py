import os
import re
import subprocess
from datetime import datetime


def srt_time_to_seconds(t: str) -> float:
    """將 srt 時間格式 00:01:02,345 轉為秒數 float"""
    hours, minutes, seconds_ms = t.split(":")
    seconds, ms = seconds_ms.split(",")
    total_seconds = (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(ms) / 1000
    )
    return total_seconds


def parse_srt(srt_path: str):
    """解析 SRT 檔案並回傳時間序列 [(index, start, end, text)]"""
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())
    subtitles = []

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            index = lines[0].strip()
            time_range = lines[1].strip()
            text = " ".join(lines[2:])
            start_time, end_time = [x.strip() for x in time_range.split("-->")]
            subtitles.append((index, start_time, end_time, text))

    return subtitles


def split_mp3_by_srt(mp3_path: str, srt_path: str, output_dir: str):
    """根據 SRT 切割 MP3 成多段音檔"""
    os.makedirs(output_dir, exist_ok=True)
    subs = parse_srt(srt_path)

    for idx, start, end, text in subs:
        start_sec = srt_time_to_seconds(start)
        end_sec = srt_time_to_seconds(end)
        duration = end_sec - start_sec

        output_file = os.path.join(output_dir, f"{int(idx):03d}.mp3")

        cmd = [
            "ffmpeg",
            "-ss",
            str(start_sec),
            "-t",
            str(duration),
            "-i",
            mp3_path,
            "-c",
            "copy",
            "-y",
            output_file,
        ]

        print(f"切割第 {idx} 段: {start} ~ {end} -> {output_file}")
        subprocess.run(cmd, capture_output=True)


# ✅ 使用範例
if __name__ == "__main__":
    mp3_path = "c:/temp/cc.mp3"  # 輸入 MP3 檔案
    srt_path = "c:/temp/cc.srt"  # 對應的 SRT 字幕檔
    output_dir = "c:/temp/cc"  # 輸出資料夾

    split_mp3_by_srt(mp3_path, srt_path, output_dir)
    print("✅ 切割完成！")
