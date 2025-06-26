import re
from typing import List


class SubtitleEntry:
    def __init__(self, index: int, start: str, end: str, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text


def time_to_ms(t: str) -> int:
    # t 例如 "00:00:01,680"
    parts = t.split(":")
    s_part, ms = parts[2].split(",")
    h = int(parts[0])
    m = int(parts[1])
    s = int(s_part)
    ms = int(ms)
    return h * 3600000 + m * 60000 + s * 1000 + ms


def ms_to_time(ms: int) -> str:
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    ms = ms % 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def parse_srt(path: str) -> List[SubtitleEntry]:
    with open(path, encoding="utf-8") as f:
        blocks = re.split(r"\n{2,}", f.read().strip())

    entries = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            index = int(lines[0])
            start, end = re.split(r"\s-->\s", lines[1])
            text = " ".join(lines[2:]).strip()
            entries.append(SubtitleEntry(index, start, end, text))
    return entries


def merge_and_split_sentences(subs: List[SubtitleEntry]) -> List[SubtitleEntry]:
    merged = []
    buffer = []
    start_time = None
    index = 1

    for sub in subs:
        if not buffer:
            start_time = sub.start
        buffer.append(sub)

        if sub.text.strip().endswith((".", "!", "?")):
            # 合併整句文本與時間
            full_text = " ".join(s.text for s in buffer)
            start_ms = time_to_ms(start_time)
            end_ms = time_to_ms(sub.end)
            total_duration = end_ms - start_ms

            # 使用正則分句
            sentences = re.split(r"(?<=[.!?])\s+", full_text.strip())
            total_chars = sum(len(s) for s in sentences)
            ratios = [len(s) / total_chars for s in sentences]

            current_start = start_ms
            for s, ratio in zip(sentences, ratios):
                duration = int(total_duration * ratio)
                current_end = current_start + duration
                merged.append(
                    SubtitleEntry(
                        index=index,
                        start=ms_to_time(current_start),
                        end=ms_to_time(current_end),
                        text=s.strip(),
                    )
                )
                index += 1
                current_start = current_end

            buffer = []  # 清空

    return merged


def write_srt(subs: List[SubtitleEntry], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for sub in subs:
            f.write(f"{sub.index}\n")
            f.write(f"{sub.start} --> {sub.end}\n")
            f.write(f"{sub.text.strip()}\n\n")


if __name__ == "__main__":
    input_path = "c:/temp/bb.srt"
    output_path = "c:/temp/normalized.srt"

    parsed = parse_srt(input_path)
    normalized = merge_and_split_sentences(parsed)
    write_srt(normalized, output_path)

    print(f"✅ 字幕正規化完成！輸出檔案：{output_path}")
