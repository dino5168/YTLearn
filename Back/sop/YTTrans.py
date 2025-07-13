import re
from googletrans import Translator

translator = Translator()


def translate_text(text, target_lang):
    if not text.strip():
        return ""
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print(f"⚠️ 翻譯失敗: {e}")
        return ""


def process_srt(input_path, output_path, target_lang):
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    output_lines = []
    buffer = []
    blocks = []
    for line in lines:
        if re.match(r"^\d+$", line.strip()):
            if buffer:
                blocks.append(list(buffer))
                buffer.clear()
        buffer.append(line)
    if buffer:
        blocks.append(list(buffer))

    total = len(blocks)
    for i, block in enumerate(blocks, start=1):
        output_lines.extend(process_block(block, target_lang))
        print(f"⏳ 處理進度: {i}/{total} ({(i/total)*100:.1f}%)", end="\r")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(output_lines)


def process_block(block_lines, target_lang):
    result = []
    text_lines = []
    block_number = ""
    timecode_line = ""

    for line in block_lines:
        if line.strip().isdigit():
            block_number = line
        elif "-->" in line:
            timecode_line = line
        else:
            text_lines.append(line.strip())

    if text_lines:
        full_text = " ".join(text_lines)
        translated = translate_text(full_text, target_lang)
        # 合併為單行字幕
        merged_line = f"{full_text}\n{translated}\n"
        result.extend([block_number, timecode_line, merged_line, "\n"])
    else:
        result.extend(block_lines)
        result.append("\n")

    return result


if __name__ == "__main__":
    print("🔠 命令列 SRT 翻譯工具（使用 googletrans，不需金鑰）")

    input_file = input("📥 請輸入 SRT 檔案路徑（例如：input.srt）：").strip()
    output_file = input("💾 請輸入輸出檔案路徑（例如：output_zh-TW.srt）：").strip()
    lang = input("🌐 請輸入目標語言（例如 zh-TW, ja, fr）：").strip()

    print(f"🚀 開始翻譯至 {lang}...")
    process_srt(input_file, output_file, lang)
    print(f"\n✅ 翻譯完成！已儲存到：{output_file}")
