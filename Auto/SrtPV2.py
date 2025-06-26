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

    result_entries = []

    # 逐個處理每個字幕條目，保持時間軸不變
    for entry in entries:
        # 清理文字，移除多餘的空格和換行
        clean_text = re.sub(r"\s+", " ", entry.text.strip())

        # 跳過音樂標記和空白內容
        if clean_text.lower() in ["[music]", "", "[音樂]"] or not clean_text:
            result_entries.append(
                SubtitleEntry(entry.index, entry.start, entry.end, clean_text)
            )
            continue

        # 對單個字幕條目進行標點修復
        try:
            punctuated = model.restore_punctuation(clean_text)
            punctuated = capitalize_first_letter(punctuated)
        except Exception as e:
            print(f"處理第 {entry.index} 條字幕時發生錯誤: {e}")
            punctuated = clean_text  # 如果處理失敗，使用原文

        # 保持原始的時間軸
        result_entries.append(
            SubtitleEntry(entry.index, entry.start, entry.end, punctuated)
        )

    return result_entries


def process_srt_file(input_path: str, output_path: str):
    try:
        entries = read_srt_file(input_path)
        print(f"讀取了 {len(entries)} 條字幕")

        punctuated_entries = punctuate_subtitles(entries)
        write_srt_file(output_path, punctuated_entries)
        print(f"✅ 已完成標點處理，輸出至：{output_path}")

    except Exception as e:
        print(f"❌ 處理過程中發生錯誤：{e}")


# === 範例使用 ===
if __name__ == "__main__":
    process_srt_file("c:/temp/input.srt", "c:/temp/output_punctuated.srt")
#
