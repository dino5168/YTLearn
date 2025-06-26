import re
from typing import List, Dict


# 定義字幕結構
class SubtitleEntry:
    def __init__(self, index: int, start: str, end: str, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text


# 讀取 SRT 檔案並解析為物件清單
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


# 合併句子並估算時間
def merge_sentences(subs: List[SubtitleEntry]) -> List[SubtitleEntry]:
    merged = []
    buffer = []
    start_time = None

    for sub in subs:
        if not buffer:
            start_time = sub.start
        buffer.append(sub)

        # 是否為句尾？
        if sub.text.strip().endswith((".", "!", "?")):
            # 合併文字
            full_text = " ".join(s.text for s in buffer)
            merged.append(
                SubtitleEntry(
                    index=len(merged) + 1, start=start_time, end=sub.end, text=full_text
                )
            )
            buffer = []  # 清空
    return merged


# 輸出為 SRT 格式
def write_srt(subs: List[SubtitleEntry], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for sub in subs:
            f.write(f"{sub.index}\n")
            f.write(f"{sub.start} --> {sub.end}\n")
            f.write(f"{sub.text.strip()}\n\n")


# 主流程
if __name__ == "__main__":
    input_path = "c:/temp/C.srt"
    output_path = "c:/temp/normalized.srt"

    parsed = parse_srt(input_path)
    merged = merge_sentences(parsed)
    write_srt(merged, output_path)

    print(f"✅ 合併完成，輸出至 {output_path}")
