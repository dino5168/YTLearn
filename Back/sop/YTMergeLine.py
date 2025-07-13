import re


def merge_srt_lines(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())  # 分段
    new_blocks = []

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            index = lines[0]
            timecode = lines[1]
            text = " ".join(line.strip() for line in lines[2:])  # 合併文字行
            new_block = f"{index}\n{timecode}\n{text}"
            new_blocks.append(new_block)
        else:
            new_blocks.append(block)

    result = "\n\n".join(new_blocks)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"\n✅ 處理完成！已儲存為：{output_path}")


# === 交談式輸入 ===
if __name__ == "__main__":
    print("🎬 字幕合併工具 - 將每段字幕文字合併為一行")
    input_path = input("請輸入字幕檔案路徑（例如 input.srt）: ").strip()
    output_path = input("請輸入輸出檔案路徑（例如 output.srt）: ").strip()

    merge_srt_lines(input_path, output_path)
