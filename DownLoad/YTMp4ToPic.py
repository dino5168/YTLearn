import pysrt
import os
import subprocess


def ensure_output_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 建立輸出目錄：{path}")
    return path


def srt_time_to_seconds(srt_time):
    return (
        srt_time.hours * 3600
        + srt_time.minutes * 60
        + srt_time.seconds
        + srt_time.milliseconds / 1000
    )


def check_ffmpeg():
    """檢查 ffmpeg 是否可用"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("✅ FFmpeg 可用")
            return True
        else:
            print("❌ FFmpeg 不可用")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ 找不到 FFmpeg，請確認已安裝並加入 PATH")
        return False


def extract_images_from_srt_midpoints(mp4_path, srt_path, output_dir="output_images"):
    ensure_output_dir(output_dir)

    # 檢查 FFmpeg
    if not check_ffmpeg():
        return False

    try:
        subs = pysrt.open(srt_path, encoding="utf-8")
        print(f"📝 成功讀取字幕檔，共 {len(subs)} 筆字幕")
    except Exception as e:
        print(f"❌ 讀取字幕檔失敗：{e}")
        return False

    success_count = 0
    error_count = 0

    for idx, sub in enumerate(subs, start=1):
        try:
            start = srt_time_to_seconds(sub.start)
            end = srt_time_to_seconds(sub.end)
            midpoint = (start + end) / 2

            output_file = os.path.join(output_dir, f"{idx:04d}.jpg")

            cmd = [
                "ffmpeg",
                "-ss",
                f"{midpoint:.3f}",  # 精準到毫秒
                "-i",
                mp4_path,
                "-frames:v",
                "1",
                "-q:v",
                "2",  # 高品質
                "-y",  # 覆蓋舊檔
                output_file,
            ]

            print(f"📸 擷取第 {idx:04d} 張圖片 @ {midpoint:.2f}s")
            print(f"   字幕內容：{sub.text.strip()[:50]}...")

            # 執行命令並捕獲輸出
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"   ✅ 成功生成 ({file_size} bytes)")
                    success_count += 1
                else:
                    print(f"   ❌ 命令執行成功但檔案不存在")
                    error_count += 1
            else:
                print(f"   ❌ FFmpeg 錯誤 (返回碼: {result.returncode})")
                # 顯示關鍵錯誤訊息
                if result.stderr:
                    stderr_lines = result.stderr.split("\n")
                    for line in stderr_lines:
                        if any(
                            keyword in line.lower()
                            for keyword in [
                                "error",
                                "invalid",
                                "failed",
                                "no such file",
                            ]
                        ):
                            print(f"   錯誤詳情: {line.strip()}")
                            break
                error_count += 1

                # 如果是前幾個就失敗，顯示命令供除錯
                if idx <= 3:
                    print(f"   除錯命令: {' '.join(cmd)}")

        except subprocess.TimeoutExpired:
            print(f"   ❌ 第 {idx} 張圖片處理超時")
            error_count += 1
        except Exception as e:
            print(f"   ❌ 第 {idx} 張圖片處理異常：{e}")
            error_count += 1

    print(f"\n📊 處理完成！成功：{success_count} 張，失敗：{error_count} 張")

    if success_count > 0:
        print(f"📁 圖片已儲存至：{os.path.abspath(output_dir)}")
        return True
    else:
        return False


def main():
    print("🎬 YouTube 字幕畫面擷取器")
    print("=" * 40)

    mp4_path = input("📥 請輸入 MP4 路徑（例如 C:/temp/video.mp4）：").strip('" ')
    srt_path = input("📥 請輸入 SRT 路徑（例如 C:/temp/subtitles.srt）：").strip('" ')
    output_dir = input("📤 請輸入輸出資料夾（預設為 output_images）：").strip('" ')

    if not output_dir:
        output_dir = "output_images"

    # 詳細檢查檔案
    print("\n🔍 檢查檔案...")
    if not os.path.isfile(mp4_path):
        print(f"❌ MP4 路徑無效：{mp4_path}")
        return
    else:
        file_size = os.path.getsize(mp4_path) / 1024 / 1024  # MB
        print(f"✅ MP4 檔案存在：{mp4_path} ({file_size:.1f} MB)")

    if not os.path.isfile(srt_path):
        print(f"❌ SRT 路徑無效：{srt_path}")
        return
    else:
        file_size = os.path.getsize(srt_path)
        print(f"✅ SRT 檔案存在：{srt_path} ({file_size} bytes)")

    # 開始處理
    print("\n🚀 開始處理...")
    success = extract_images_from_srt_midpoints(mp4_path, srt_path, output_dir)

    if success:
        print("\n🎉 處理完成！可以檢查輸出資料夾中的圖片")
    else:
        print("\n😞 處理失敗，請檢查上述錯誤訊息")


if __name__ == "__main__":
    main()
