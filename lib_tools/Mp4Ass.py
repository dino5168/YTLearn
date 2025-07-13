import subprocess
from pathlib import Path
import sys
import time


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return True
    except Exception:
        return False


def normalize_path_for_ffmpeg(path: Path) -> str:
    if sys.platform == "win32":
        return str(path.resolve()).replace("\\", "/").replace(":", "\\:")
    return str(path.resolve())


def show_progress(seconds: int):
    for i in range(seconds):
        bar = "█" * (i + 1) + "-" * (seconds - i - 1)
        print(f"\r⏳ 處理中 [{bar}] {i+1}/{seconds} 秒", end="")
        time.sleep(1)
    print()


def embed_subtitles_with_background(mp4_path: str, ass_path: str, output_path: str):
    mp4_file = Path(mp4_path)
    ass_file = Path(ass_path)
    output_file = Path(output_path)

    if not mp4_file.exists():
        print(f"❌ 找不到影片：{mp4_file}")
        return False
    if not ass_file.exists():
        print(f"❌ 找不到字幕檔案：{ass_file}")
        return False

    video_input = str(mp4_file.resolve())
    subtitle_input = normalize_path_for_ffmpeg(ass_file)

    # 背景 + 字幕一起
    filter_str = f"drawbox=y=ih*2/3:h=ih/3:color=navy@0.6:t=fill,ass='{subtitle_input}'"

    cmd = [
        "ffmpeg",
        "-i",
        video_input,
        "-vf",
        filter_str,
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

    print("\n🔧 開始轉檔，請稍候...")
    print(f"📋 FFmpeg 濾鏡：{filter_str}")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    show_progress(5)  # 模擬進度條 5 秒

    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("✅ 成功嵌入字幕與背景色塊！")
        print(f"📁 影片已輸出至：{output_file}")
        return True
    else:
        print("❌ 發生錯誤：")
        print(stderr.decode())
        return False


def main():
    print("🎬 MP4 + ASS 字幕燒錄工具（含底部背景）")
    print("=" * 40)

    if not check_ffmpeg():
        print("❌ 請先安裝 FFmpeg：https://ffmpeg.org/")
        return

    mp4_path = input("📥 請輸入 MP4 影片路徑：").strip().strip('"')
    ass_path = input("📝 請輸入 ASS 字幕路徑：").strip().strip('"')

    default_output = (
        Path(mp4_path)
        .with_stem(Path(mp4_path).stem + "_with_bg_sub")
        .with_suffix(".mp4")
    )
    output_path = input(f"📤 請輸入輸出檔案（預設: {default_output}）：").strip().strip(
        '"'
    ) or str(default_output)

    success = embed_subtitles_with_background(mp4_path, ass_path, output_path)

    if success:
        print("🎉 完成！")
    else:
        print("⚠️ 請檢查路徑或 ASS 字幕內容是否有誤")


if __name__ == "__main__":
    main()
