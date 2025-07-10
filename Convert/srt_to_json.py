import re
import json


def parse_srt(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(\d+)\s+"
        r"(\d{2}:\d{2}:\d{2},\d{3})\s-->\s"
        r"(\d{2}:\d{2}:\d{2},\d{3})\s+"
        r"(.*?)(?=\n\d+\n|\Z)",
        re.DOTALL,
    )

    subs = []
    for match in pattern.findall(content):
        seq, start, end, text = match
        text = text.replace("\n", " ").strip()
        subs.append(
            {"seq": int(seq), "start_time": start, "end_time": end, "text": text}
        )
    return subs


def combine_srt_to_json(english_path, chinese_path, output_path, video_id):
    english_srt = parse_srt(english_path)
    chinese_srt = parse_srt(chinese_path)

    if len(english_srt) != len(chinese_srt):
        raise ValueError("字幕數量不一致")

    subtitles = []
    for en, zh in zip(english_srt, chinese_srt):
        subtitles.append(
            {
                "seq": en["seq"],
                "start_time": en["start_time"],
                "end_time": en["end_time"],
                "ex_text": en["text"],
                "zh_text": zh["text"],
            }
        )

    # 建立包含 video_id 的完整結構
    combined = {"video_id": video_id, "subtitles": subtitles}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"✅ 已輸出 JSON 檔案：{output_path}")
    print(f"📹 影片 ID：{video_id}")


# ✅ 執行
if __name__ == "__main__":
    combine_srt_to_json(
        "c:/temp/b/Lady.srt",
        "c:/temp/b/Lady.tw.srt",
        "c:/temp/b/Lady_combined.json",
        "IArxapKwXLM",  # 新增的 video_id 參數
    )
