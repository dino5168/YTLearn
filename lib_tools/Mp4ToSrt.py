#!/usr/bin/env python3
"""
FFmpeg 字幕嵌入工具（含底部深藍背景 + 中英文分色樣式）
"""

import subprocess
from pathlib import Path
import sys
import re

from pysubs2 import SSAFile, Color, Alignment


def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


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

    # 樣式：英文（白色）
    english_style = subs.styles["English"]
    english_style.fontname = "Arial"
    english_style.fontsize = 26
    english_style.primarycolor = Color(255, 255, 255, 0)  # White
    english_style.outlinecolor = Color(0, 0, 0, 0)  # Black
    english_style.backcolor = Color(0, 0, 139, 180)  # Navy blue, 180 alpha
    english_style.bold = True
    english_style.outline = 2
    english_style.shadow = 1
    english_style.alignment = Alignment.BOTTOM_CENTER
    english_style.marginv = 60
    english_style.marginl = 50
    english_style.marginr = 50

    # 樣式：中文（黃色）
    chinese_style = english_style.copy()
    chinese_style.primarycolor = Color(102, 255, 255, 0)  # Yellow (RGB: 102,255,255)
    subs.styles["Chinese"] = chinese_style

    # 加入字幕事件
    for line in srt_subs:
        text = line.text.strip()
        if not text:
            continue

        clean_text = re.sub(r"<[^>]+>", "", text)
        new_line = line.copy()

        # Determine the style and corresponding primary color for the override tag
        if has_chinese(clean_text):
            new_line.style = "Chinese"
            # Color(102, 255, 255, 0) -> RGB (102, 255, 255) -> BGR (255, 255, 102) -> H66FFFF&
            primary_color_hex = "H66FFFF&"
        else:
            new_line.style = "English"
            # Color(255, 255, 255, 0) -> RGB (255, 255, 255) -> BGR (255, 255, 255) -> HFFFFFF&
            primary_color_hex = "HFFFFFF&"

        # \an2: bottom center alignment
        # \bord2: 2px border
        # \shad1: 1px shadow
        # \3c&H000000&: Outline color (Black)
        # \4c&H8B0000&: Background color (Navy Blue, BGR 00008B)
        # \4a&H60&: Background alpha (Transparency, 96/255)
        # \1c&HXXXXXX&: Primary text color (White or Yellow)
        new_line.text = f"{{\\an2\\bord2\\shad1\\3c&H000000&\\4c&H8B0000&\\4a&H60&\\1c{primary_color_hex}}}{text}"

        subs.append(new_line)

    subs.save(str(ass_file))
    print(f"✅ 產生 ASS 字幕檔案：{ass_file}")
    return ass_file


def embed_ass_subtitles(mp4_path: str, ass_path: str, output_path: str) -> bool:
    mp4_file = Path(mp4_path)
    ass_file = Path(ass_path)
    output_file = Path(output_path)

    if not mp4_file.exists():
        print(f"❌ 找不到影片：{mp4_file}")
        return False
    if not ass_file.exists():
        print(f"❌ 找不到字幕檔：{ass_file}")
        return False

    print(f"\n📹 影片：{mp4_file}")
    print(f"📝 字幕：{ass_file}")
    print(f"🎬 輸出：{output_file}")
    print("-" * 50)

    try:
        video_input = str(mp4_file.resolve())
        subtitle_input = str(ass_file.resolve())

        if sys.platform == "win32":
            subtitle_input = subtitle_input.replace("\\", "/").replace(":", "\\:")

        # 合併 drawbox + ass 濾鏡
        drawbox_filter = "drawbox=y=ih*2/3:h=ih/3:color=navy@0.6:t=fill"
        ass_filter = f"ass='{subtitle_input}'"
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

        print("🔄 開始轉檔中...")
        print(f"📋 使用濾鏡：{full_filter}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 成功嵌入字幕！")
            print(f"📁 輸出影片：{output_file}")

            if mp4_file.exists() and output_file.exists():
                original_size = mp4_file.stat().st_size / (1024 * 1024)
                output_size = output_file.stat().st_size / (1024 * 1024)
                print(f"📊 原始大小：{original_size:.1f} MB")
                print(f"📊 輸出大小：{output_size:.1f} MB")
            return True
        else:
            print("❌ FFmpeg 錯誤：")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        return False


def main():
    print("🎬 字幕嵌入工具（底部深藍背景 + 中英文分色）")
    print("=" * 50)

    if not check_ffmpeg():
        print("❌ 請先安裝 FFmpeg：https://ffmpeg.org/download.html")
        sys.exit(1)

    mp4_path = input("📥 請輸入 MP4 影片路徑：").strip().strip('"')
    srt_path = input("📥 請輸入 SRT 字幕檔路徑：").strip().strip('"')

    if not Path(mp4_path).exists():
        print(f"❌ 找不到影片：{mp4_path}")
        return
    if not Path(srt_path).exists():
        print(f"❌ 找不到字幕：{srt_path}")
        return

    default_output = (
        Path(mp4_path)
        .with_stem(Path(mp4_path).stem + "_with_subtitles")
        .with_suffix(".mp4")
    )
    output_path = input(
        f"📤 請輸入輸出檔案路徑（預設: {default_output}）："
    ).strip().strip('"') or str(default_output)

    print("\n🔁 轉換字幕格式中（SRT → ASS）...")
    ass_file = convert_srt_to_ass(srt_path)

    success = embed_ass_subtitles(mp4_path, str(ass_file), output_path)
    if success:
        print("\n🎉 字幕處理完成！")
        print(f"📁 檔案已儲存：{output_path}")
    else:
        print("\n⚠️ 嵌入失敗，請檢查錯誤訊息。")
        print("\n💡 常見排查：")
        print("1. 確認 FFmpeg 是否已安裝")
        print("2. 確認路徑無誤")
        print("3. 確認字幕格式正確（UTF-8 編碼）")
        print("4. 嘗試用 VLC 播放輸出檔案")


if __name__ == "__main__":
    main()
