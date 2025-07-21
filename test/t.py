# 重新整理 字幕檔
import re
from datetime import timedelta


def parse_timestamp(timestamp: str) -> float:
    """將 SRT 時間格式轉為秒數"""
    h, m, s_ms = timestamp.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def format_timestamp(seconds: float) -> str:
    """將秒數轉回 SRT 時間格式"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    ms = int((td.total_seconds() - total_seconds) * 1000)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def merge_srt_to_sentence_srt(input_srt_path: str, output_srt_path: str):
    with open(input_srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())

    merged_segments = []
    buffer_text = ""
    buffer_start = None
    buffer_end = None

    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue

        time_range = lines[1]
        text = " ".join(lines[2:]).strip()

        start_str, end_str = time_range.split(" --> ")
        start_sec = parse_timestamp(start_str)
        end_sec = parse_timestamp(end_str)

        if buffer_text == "":
            buffer_start = start_sec

        buffer_text += (" " if buffer_text else "") + text
        buffer_end = end_sec

        if re.search(r'[.!?]["”]?$|\w\.\s*$', text):
            merged_segments.append((buffer_start, buffer_end, buffer_text.strip()))
            buffer_text = ""
            buffer_start = None
            buffer_end = None

    # 殘留最後一句
    if buffer_text:
        merged_segments.append((buffer_start, buffer_end, buffer_text.strip()))

    # 寫入新的 SRT 檔案
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for idx, (start, end, text) in enumerate(merged_segments, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")

    print(f"[輸出完成] 新的合併字幕已寫入：{output_srt_path}")


if __name__ == "__main__":
    srt = merge_srt_to_sentence_srt(r"c:/temp/0719/1.srt", r"c:/temp/0719/1_m.srt")
    print(srt)
