import re


def remove_punctuation(text):
    # 移除標點符號，只保留中英文與數字
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", text)


def split_text_by_lengths(text, lengths):
    """根據 lengths 切割 text"""
    segments = []
    index = 0
    for length in lengths:
        segments.append(text[index : index + length])
        index += length
    return segments


def main():
    soruceTxt = r"c:\ai\html\source.txt"
    soruceSrt = r"c:\ai\html\source.srt"

    with open(soruceTxt, "r", encoding="utf-8") as f:
        full_text = f.read()
    full_text_clean = remove_punctuation(full_text)

    with open(soruceSrt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_block = []
    text_lengths = []
    cleaned_texts = []
    blocks = []

    for line in lines:
        if line.strip() == "":
            if current_block:
                text_lines = [
                    l
                    for l in current_block
                    if not l.strip().isdigit() and "-->" not in l
                ]
                original_text = "".join(text_lines).strip()
                clean_text = remove_punctuation(original_text)
                text_lengths.append(len(clean_text))
                cleaned_texts.append(clean_text)
                blocks.append((len(clean_text), original_text.strip()))
                current_block = []
        else:
            current_block.append(line)

    if current_block:
        text_lines = [
            l for l in current_block if not l.strip().isdigit() and "-->" not in l
        ]
        original_text = "".join(text_lines).strip()
        clean_text = remove_punctuation(original_text)
        text_lengths.append(len(clean_text))
        cleaned_texts.append(clean_text)
        blocks.append((len(clean_text), original_text.strip()))

    full_len = len(full_text_clean)
    total_sub_len = sum(text_lengths)

    if total_sub_len != full_len:
        print(
            f"❌ 錯誤：source.txt 有 {full_len} 字，srt 淨字數為 {total_sub_len} 字。\n"
        )
        print("🔍 以下為字數不一致的段落：")

        # 嘗試從 source.txt 根據 srt 的段落長度來切分比較
        try:
            target_segments = split_text_by_lengths(full_text_clean, text_lengths)
            for idx, (clean_len, srt_text) in enumerate(blocks):
                expected_text = target_segments[idx]
                if len(expected_text) != clean_len:
                    print(
                        f"[{idx+1:03}] 預期 {len(expected_text)} 字，實際 {clean_len} 字 → {srt_text}"
                    )
        except:
            print("⚠️ 無法對應切分，請手動檢查")
    else:
        print("✅ 所有段落字數一致！")


if __name__ == "__main__":
    main()
