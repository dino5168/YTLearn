import re
import os
import argparse
from difflib import SequenceMatcher


def read_file(file_path, encoding="utf-8"):
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        for enc in ["utf-8-sig", "big5", "cp950", "gbk"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    print(f"使用 {enc} 編碼讀取檔案: {file_path}")
                    return f.read()
            except:
                continue
        raise Exception(f"無法讀取檔案 {file_path}，請檢查編碼")
    except FileNotFoundError:
        raise Exception(f"找不到檔案: {file_path}")


def parse_srt(srt_content):
    srt_content = srt_content.replace("\r\n", "\n").replace("\r", "\n")
    blocks = srt_content.strip().split("\n\n")
    subtitles = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            try:
                index = int(lines[0])
                timestamp = lines[1]
                text = " ".join(lines[2:])
                subtitles.append({"index": index, "timestamp": timestamp, "text": text})
            except ValueError:
                continue
    return subtitles


def clean_text(text):
    return re.sub(r"[^\w\u4e00-\u9fff]", "", text).lower()


def find_best_match(source_text, subtitle_text):
    cleaned_subtitle = clean_text(subtitle_text)
    cleaned_source = clean_text(source_text)
    if not cleaned_subtitle:
        return subtitle_text, 0.0
    best_ratio = 0.0
    best_start = 0
    for i in range(len(cleaned_source) - len(cleaned_subtitle) + 1):
        segment = cleaned_source[i : i + len(cleaned_subtitle)]
        ratio = SequenceMatcher(None, cleaned_subtitle, segment).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_start = i
    if best_ratio >= 0.6:
        corrected = (
            get_original_segment(source_text, best_start, len(cleaned_subtitle))
            or subtitle_text
        )
        return corrected, best_ratio
    return subtitle_text, best_ratio


def get_original_segment(source_text, start_pos, length):
    char_count = 0
    start_original = 0
    for i, char in enumerate(source_text):
        if re.match(r"[\w\u4e00-\u9fff]", char):
            if char_count == start_pos:
                start_original = i
                break
            char_count += 1
    char_count = 0
    end_original = start_original
    for i in range(start_original, len(source_text)):
        if re.match(r"[\w\u4e00-\u9fff]", source_text[i]):
            char_count += 1
            if char_count >= length:
                end_original = i + 1
                break
        end_original = i + 1
    return source_text[start_original:end_original].strip()


def generate_corrected_srt(subtitles):
    output = []
    for sub in subtitles:
        output.append(str(sub["index"]))
        output.append(sub["timestamp"])
        output.append(sub["text"])
        output.append("")
    return "\n".join(output)


def generate_report(subtitles, original_subtitles):
    lines = []
    for sub, original in zip(subtitles, original_subtitles):
        if sub["text"] != original["text"]:
            lines.append(f"[{sub['index']}]")
            lines.append(f"原字幕：{original['text']}")
            lines.append(f"校正後：{sub['text']}")
            lines.append("")
    return "\n".join(lines)


def correct_srt(source_text, srt_content):
    subtitles = parse_srt(srt_content)
    original_subtitles = [sub.copy() for sub in subtitles]
    for sub in subtitles:
        corrected_text, _ = find_best_match(source_text, sub["text"])
        sub["text"] = corrected_text
    return subtitles, original_subtitles


def main():
    parser = argparse.ArgumentParser(
        description="字幕校正工具：根據原文修正 SRT 並產生報告"
    )
    parser.add_argument("source_file", help="原文檔案路徑")
    parser.add_argument("srt_file", help="SRT 字幕檔案路徑")
    parser.add_argument(
        "-o", "--output", help="輸出校正後 SRT 路徑（預設為 *_corrected.srt）"
    )
    args = parser.parse_args()

    source_text = read_file(args.source_file)
    srt_content = read_file(args.srt_file)

    corrected_subs, original_subs = correct_srt(source_text, srt_content)
    corrected_srt = generate_corrected_srt(corrected_subs)
    report = generate_report(corrected_subs, original_subs)

    # 輸出路徑處理
    base_name = os.path.splitext(args.srt_file)[0]
    output_srt_path = args.output or base_name + "_corrected.srt"
    report_path = base_name + "_report.txt"

    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(corrected_srt)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 已輸出校正後 SRT：{output_srt_path}")
    print(f"📄 已產生校正報告：{report_path}")


if __name__ == "__main__":
    main()
