#!/usr/bin/env python3
"""
互動式 FFmpeg 字幕嵌入工具
使用方式：直接執行後依提示輸入
"""

import subprocess
from pathlib import Path


def check_ffmpeg() -> bool:
    """檢查 FFmpeg 是否可用"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def input_path(path: Path) -> str:
    """用於 -i 或輸出檔案路徑，不進行 escape"""
    return str(path.resolve().as_posix())


def subtitles_filter_path(path: Path) -> str:
    """用於 subtitles=... 的路徑，需 escape 冒號"""
    return str(path.resolve().as_posix()).replace(":", "\\:")


def embed_subtitles_with_style(mp4_path: str, srt_path: str, output_path: str) -> bool:
    """執行 FFmpeg 將字幕嵌入影片，附樣式"""
    mp4_file = Path(mp4_path)
    srt_file = Path(srt_path)
    output_file = Path(output_path)

    if not mp4_file.exists():
        print(f"❌ 找不到影片檔案：{mp4_file}")
        return False

    if not srt_file.exists():
        print(f"❌ 找不到字幕檔案：{srt_file}")
        return False

    print(f"\n📹 輸入影片：{mp4_file}")
    print(f"📝 字幕檔案：{srt_file}")
    print(f"🎬 輸出檔案：{output_file}")
    print("-" * 50)

    subtitle_style = (
        "FontName=Arial;"
        "FontSize=24;"
        "PrimaryColour=&HFFFFFF;"
        "OutlineColour=&H000000;"
        "BackColour=&H80000000;"
        "Bold=1;"
        "BorderStyle=1;"
        "Outline=2;"
        "Alignment=2;"
        "MarginV=50"
    )

    try:
        video_input = input_path(mp4_file)
        subtitle_input = subtitles_filter_path(srt_file)

        subtitle_filter = f"subtitles='{subtitle_input}':force_style='{subtitle_style}'"

        cmd = [
            "ffmpeg",
            "-i",
            video_input,
            "-vf",
            subtitle_filter,
            "-c:a",
            "copy",
            "-y",
            str(output_file),
        ]

        print("🔄 開始處理中...\n")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 字幕嵌入成功！")
            print(f"📁 輸出檔案：{output_file}")
            original_size = mp4_file.stat().st_size / (1024 * 1024)
            output_size = output_file.stat().st_size / (1024 * 1024)
            print(f"📊 原始大小：{original_size:.1f} MB")
            print(f"📊 輸出大小：{output_size:.1f} MB")
            return True
        else:
            print("❌ 字幕嵌入失敗")
            print("🧾 FFmpeg 錯誤訊息如下：\n")
            print(result.stderr)
            print("\n💡 提示：")
            print("  1️⃣ 確認字幕檔案編碼為 UTF-8（無 BOM）")
            print("  2️⃣ 確保字幕與影片路徑中無特殊字元（如空格、#、:）")
            print("  3️⃣ 字幕檔名建議使用英文與數字，避免中文")
            return False

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        return False


def main():
    print("🎬 FFmpeg 字幕嵌入工具（互動模式）")
    print("=" * 40)

    if not check_ffmpeg():
        print("❌ 找不到 FFmpeg，請先安裝：https://ffmpeg.org/download.html")
        return

    mp4_path = input("📥 請輸入 MP4 影片檔案路徑：").strip().strip('"')
    srt_path = input("📥 請輸入 SRT 字幕檔案路徑：").strip().strip('"')

    default_output = (
        Path(mp4_path)
        .with_stem(Path(mp4_path).stem + ".with_subtitles")
        .with_suffix(".mp4")
    )
    output_path = input(
        f"📤 請輸入輸出檔案路徑（預設: {default_output}）："
    ).strip().strip('"') or str(default_output)

    success = embed_subtitles_with_style(mp4_path, srt_path, output_path)
    if not success:
        print("\n⚠️ 處理失敗，請依提示排查後重試。")


if __name__ == "__main__":
    main()
