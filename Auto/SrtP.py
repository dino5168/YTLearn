import re
from deepmultilingualpunctuation import PunctuationModel
from typing import List


class SubtitleEntry:
    def __init__(self, index: int, start: str, end: str, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text


def read_srt_file(file_path: str) -> List[SubtitleEntry]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    blocks = re.split(r"\n{2,}", content.strip())
    for block in blocks:
        lines = block.splitlines()
        if len(lines) >= 3:
            index = int(lines[0])
            times = lines[1]
            text = " ".join(lines[2:])
            start, end = times.split(" --> ")
            entries.append(SubtitleEntry(index, start, end, text.strip()))
    return entries


def write_srt_file(file_path: str, entries: List[SubtitleEntry]):
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"{entry.index}\n")
            f.write(f"{entry.start} --> {entry.end}\n")
            f.write(f"{entry.text}\n\n")


def capitalize_first_letter(text: str) -> str:
    # 將每個句子的第一個英文單字首字母大寫
    sentences = re.split(r"(?<=[.!?]) +", text)
    return " ".join(s.capitalize() for s in sentences)


def punctuate_subtitles(entries: List[SubtitleEntry]) -> List[SubtitleEntry]:
    model = PunctuationModel()
    full_text = " ".join(entry.text for entry in entries)
    punctuated = model.restore_punctuation(full_text)
    punctuated = capitalize_first_letter(punctuated)

    # 平均分配標點後的文字回到每一段
    words = punctuated.split()
    total_words = len(words)
    avg_len = total_words // len(entries)

    result_entries = []
    idx = 0
    for i, entry in enumerate(entries):
        if i == len(entries) - 1:
            chunk = words[idx:]
        else:
            chunk = words[idx : idx + avg_len]
        entry.text = " ".join(chunk)
        result_entries.append(entry)
        idx += avg_len
    return result_entries


def process_srt_file(input_path: str, output_path: str):
    entries = read_srt_file(input_path)
    punctuated_entries = punctuate_subtitles(entries)
    write_srt_file(output_path, punctuated_entries)
    print(f"✅ 已完成標點處理，輸出至：{output_path}")


# === 範例使用 ===
if __name__ == "__main__":
    process_srt_file("c:/temp/input.srt", "c:/temp/output_punctuated.srt")
