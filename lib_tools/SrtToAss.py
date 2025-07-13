import re
from pathlib import Path
import pysubs2
from pysubs2 import SSAFile, SSAEvent, SSAStyle, Color, Alignment
import textwrap


def wrap_text(text: str, max_width: int = 50) -> str:
    """處理文字折行，英文按單詞折行，中文按字元折行"""
    if not text:
        return ""

    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    total_chars = len(text)

    if chinese_chars > total_chars * 0.5:
        # 中文折行：每行最多 max_width//2 個字元
        lines = []
        current_line = ""
        for char in text:
            if len(current_line) >= max_width // 2:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char
        if current_line:
            lines.append(current_line)
        return r"\N".join(lines)
    else:
        # 英文折行：使用 textwrap 按單詞折行
        wrapped = textwrap.fill(
            text, width=max_width, break_long_words=False, break_on_hyphens=False
        )
        return wrapped.replace("\n", r"\N")


def srt_en_zh_to_ass(srt_path: str, ass_path: str):
    print(f"📥 開始讀取 SRT 檔案：{srt_path}")
    srt_file = Path(srt_path)
    ass_file = Path(ass_path)

    subs = pysubs2.load(str(srt_file), encoding="utf-8")

    # 建立 ASS 檔
    ass_subs = SSAFile()
    ass_subs.info["PlayResX"] = "1920"
    ass_subs.info["PlayResY"] = "1080"
    ass_subs.styles.clear()

    # 修改後樣式：底部中上對齊（約佔畫面底下 1/3 高處）
    base_style = SSAStyle()
    base_style.fontname = "Arial"
    base_style.fontsize = 56
    base_style.bold = True
    base_style.alignment = Alignment.BOTTOM_CENTER  # \an2
    base_style.marginv = 100  # Y 軸抬高約 1/3 高度
    base_style.marginl = 60
    base_style.marginr = 60
    base_style.outline = 3
    base_style.shadow = 2
    base_style.backcolor = Color(36, 36, 88, 200)  # 深藍底（透明）
    base_style.outlinecolor = Color(0, 0, 0, 0)
    base_style.primarycolor = Color(255, 255, 255, 0)  # 白色

    ass_subs.styles["Default"] = base_style

    print("🔧 處理中英文字幕...")
    for line in subs:
        lines = re.split(r"\r?\n", line.text.strip())
        if len(lines) >= 2:
            en = lines[0].strip()
            zh = lines[1].strip()
        elif len(lines) == 1:
            en, zh = lines[0].strip(), ""
        else:
            continue

        # 折行處理
        en_wrapped = wrap_text(en, max_width=50) if en else ""
        zh_wrapped = wrap_text(zh, max_width=25) if zh else ""

        # 全部都白字
        combined_text = (
            r"{\c&HFFFFFF&}"
            + en_wrapped
            + r"\N"
            + r"\N"
            + r"{\c&HFFFFFF&}"
            + zh_wrapped
        )

        event = SSAEvent(
            start=line.start, end=line.end, text=combined_text, style="Default"
        )
        ass_subs.append(event)

    ass_subs.save(str(ass_file))
    print(f"✅ 已輸出 ASS 檔案：{ass_file}")


def main():
    print("🎬 歡迎使用 SRT 轉 ASS 字幕工具")
    print("📌 英文白字 / 中文白字 + 深藍底，顯示於底部偏上（1/3 高）")
    input_path = input("請輸入 SRT 檔案路徑：").strip().strip('"')
    output_path = input("請輸入輸出 ASS 檔案路徑（如 output.ass）：").strip().strip('"')

    if not Path(input_path).exists():
        print(f"❌ 找不到檔案：{input_path}")
        return

    srt_en_zh_to_ass(input_path, output_path)


if __name__ == "__main__":
    main()
