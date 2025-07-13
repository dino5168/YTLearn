import re
from datetime import datetime

TIME_FORMAT = "%H:%M:%S,%f"


def parse_time(t):
    return datetime.strptime(t, TIME_FORMAT)


def format_time(t):
    return t.strftime(TIME_FORMAT)[:-3]  # 去掉最後3位微秒，只留到毫秒


def read_srt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 用正則切割每段字幕
    blocks_raw = re.split(r"\n\s*\n", content.strip())
    blocks = []

    for block in blocks_raw:
        lines = block.splitlines()
        if len(lines) < 3:
            continue  # 不完整跳過
        idx = lines[0].strip()
        times = lines[1].strip()
        en = lines[2].strip()
        zh = lines[3].strip() if len(lines) > 3 else ""

        m = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", times
        )
        if not m:
            continue  # 格式錯誤跳過
        start = parse_time(m.group(1))
        end = parse_time(m.group(2))

        blocks.append({"idx": idx, "start": start, "end": end, "en": en, "zh": zh})

    return blocks


def adjust_end_times(blocks):
    for i in range(len(blocks) - 1):
        blocks[i]["end"] = blocks[i + 1]["start"]
    # 最後一段不變
    return blocks


def write_srt(blocks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for b in blocks:
            f.write(f"{b['idx']}\n")
            f.write(f"{format_time(b['start'])} --> {format_time(b['end'])}\n")
            f.write(f"{b['en']}\n")
            if b["zh"]:
                f.write(f"{b['zh']}\n")
            f.write("\n")


def main():
    input_path = input("請輸入原始 SRT 檔案路徑：")
    output_path = input("請輸出新的 SRT 檔案路徑：")

    blocks = read_srt(input_path)
    blocks = adjust_end_times(blocks)
    write_srt(blocks, output_path)

    print(f"完成調整並輸出到 {output_path}")


if __name__ == "__main__":
    main()
