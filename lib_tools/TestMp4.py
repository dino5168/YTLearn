#!/usr/bin/env python3
"""
將 SRT 字幕轉換為 ASS（中英文分色樣式）並在影片下方加入深藍底色區塊（高度為畫面 1/3）
"""

import subprocess
from pathlib import Path
import sys
import re
from pysubs2 import SSAFile, SSAStyle, Color, Alignment


def has_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def convert_srt_to_ass(srt_path: str) -> Path:
    srt_file = Path(srt_path)
    ass_file = srt_file.with_suffix(".ass")

    subs = SSAFile()
    srt_subs = SSAFile.load(str(srt_file), encoding="utf-8")

    subs.info["PlayResX"] = "1920"
    subs.info["PlayResY"] = "1080"
    subs.styles.clear()

    # 建立 English 樣式
    english_style = SSAStyle()
    english_style.fontname = "Arial"
    english_style.fontsize = 26
    english_style.primarycolor = Color(255, 255, 255, 0)  # 白色
    english_style.outlinecolor = Color(0, 0, 0, 0)  # 黑邊
    english_style.backcolor = Color(0, 0, 139, 180)  # 深藍底透明
    english_style.bold = True
    english_style.outline = 2
    english_style.shadow = 1
    english_style.alignment = Alignment.BOTTOM_CENTER
    english_style.marginv = 60
    english_style.marginl = 50
    english_style.marginr = 50

    subs.styles["English"] = english_style

    # 建立 Chinese 樣式（亮藍字）
    chinese_style = english_style.copy()
    chinese_style.primarycolor = Color(102, 255, 255, 0)
    subs.styles["Chinese"] = chinese_style

    # 加入字幕事件
    for line in srt_subs:
        text = line.text.strip()
        if not text:
            continue

        clean_text = re.sub(r"<[^>]+>", "", text)
        new_line = line.copy()

        if has_chinese(clean_text):
            new_line.style = "Chinese"
            color_tag = "H66FFFF&"
        else:
            new_line.style = "English"
            color_tag = "HFFFFFF&"

        # \an2=底部置中，設定文字樣式
        new_line.text = f"{{\\an2\\bord2\\shad1\\3c&H000000&\\4c&H8B0000&\\4a&H60&\\1c{color_tag}}}{text}"
        subs.append(new_line)

    subs.save(str(ass_file))
    print(f"✅ 產生 ASS 字幕檔案：{ass_file}")
    return ass_file


def embed_ass_with_overlay(mp4_path: str, ass_path: str, output_path: str) -> bool:
    mp4_file = Path(mp4_path)
    ass_file = Path(ass_path)
    output_file = Path(output_path)

    if not mp4_file.exists():
        print(f"❌ 找不到影片：{mp4_file}")
        return False
    if not ass_file.exists():
        print(f"❌ 找不到字幕檔：{ass_file}")
        return False

    video_input = str(mp4_file.resolve())
    subtitle_input = str(ass_file.resolve())

    if sys.platform == "win32":
        # ✅ 安全處理 Windows 路徑給 FFmpeg 使用
        video_input = video_input.replace("\\", "/")
        subtitle_input = subtitle_input.replace("\\", "/").replace(":", "\\:")

    # ✅ drawbox: 畫面下方 1/3 高度的 navy 半透明區塊
    drawbox_filter = "drawbox=y=ih*2/3:h=ih/3:color=navy@0.6:t=fill"
    ass_filter = f"ass={subtitle_input}"  # ✅ 避免包單引號，避免解析錯誤
    full_filter = f"{drawbox_filter},{ass_filter}"

    cmd = [
        "ffmpeg",
        "-i",
        video_input,
        "-vf",
        full_filter,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        "-y",
        str(output_file),
    ]

    print("\n🔧 執行 FFmpeg：")
    print(" ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ 成功輸出影片：{output_file}")
        return True
    else:
        print("❌ FFmpeg 錯誤：")
        print(result.stderr)
        return False


def main():
    print("🎬 字幕 + 深藍底 合成工具")
    print("=" * 40)

    mp4_path = input("📥 請輸入 MP4 路徑：").strip().strip('"')
    srt_path = input("📥 請輸入 SRT 字幕檔路徑：").strip().strip('"')

    if not Path(mp4_path).exists():
        print("❌ 找不到 MP4 影片")
        return
    if not Path(srt_path).exists():
        print("❌ 找不到 SRT 字幕")
        return

    default_output = Path(mp4_path).with_stem(
        Path(mp4_path).stem + "_with_subtitles_overlay"
    )
    output_path = input(f"📤 請輸入輸出路徑（預設: {default_output}）：").strip().strip(
        '"'
    ) or str(default_output)

    print("\n🔁 開始轉換字幕...")
    ass_file = convert_srt_to_ass(srt_path)

    print("🎞️ 開始合成影片 + 底色 + 字幕...")
    success = embed_ass_with_overlay(mp4_path, str(ass_file), output_path)

    if success:
        print("\n🎉 成功完成！")
    else:
        print("\n⚠️ 嵌入失敗，請檢查 FFmpeg 錯誤訊息")


if __name__ == "__main__":
    main()
