import pysrt
import os
import subprocess
import re
import tempfile


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


def ultra_clean_subtitle_text(text):
    """超強字幕文字清理，移除所有可能導致問題的字符"""
    if not text:
        return "無字幕"

    # 移除HTML標籤
    text = re.sub(r"<[^>]+>", "", text)

    # 移除換行和回車
    text = text.replace("\n", " ").replace("\r", " ")

    # 移除所有可能有問題的字符，只保留基本字符
    # 保留：中文、英文、數字、基本標點
    allowed_chars = re.compile(
        r'[^\u4e00-\u9fff\u3400-\u4dbf\w\s，。！？；：、（）【】「」《》〈〉,.!?;:()\[\]{}<>"\'-]'
    )
    text = allowed_chars.sub("", text)

    # 清理多餘空格
    text = " ".join(text.split())

    # 如果清理後是空的，提供預設文字
    if not text.strip():
        return "字幕內容"

    # 限制長度
    if len(text) > 80:
        text = text[:77] + "..."

    return text.strip()


def create_safe_subtitle_file(text, index):
    """建立安全的字幕檔案"""
    try:
        # 使用系統暫存目錄
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"ffmpeg_subtitle_{index}_{os.getpid()}.txt")

        with open(temp_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

        return temp_file
    except Exception as e:
        print(f"   ⚠️ 無法建立暫存檔：{e}")
        return None


def get_video_info(mp4_path):
    """獲取影片資訊"""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            mp4_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ 影片檔案格式正常")
            return True
    except:
        pass

    print("⚠️ 無法獲取影片資訊，但繼續嘗試處理")
    return True


def extract_images_with_robust_subtitles(
    mp4_path, srt_path, output_dir="output_images"
):
    ensure_output_dir(output_dir)

    # 檢查影片
    get_video_info(mp4_path)

    # 嘗試多種字型
    font_candidates = [
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenRyuMin-B.ttf",
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenRyuMin-M.ttf",
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenRyuMin-R.ttf",
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenRyuMin-Bold.ttf",
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenRyuMin-Light.ttf",
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenRyuMin-Heavy.ttf",
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\msjh.ttc",  # 微軟正黑體
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\simsun.ttc",  # 新細明體
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\arial.ttf",  # Arial
        r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\calibri.ttf",  # Calibri
        "arial",  # 系統預設
    ]

    selected_font = None
    for font in font_candidates:
        if font == "arial" or os.path.exists(font):
            selected_font = font
            print(f"🔤 使用字型：{font}")
            break

    if not selected_font:
        selected_font = "arial"
        print("🔤 使用系統預設字型")

    try:
        subs = pysrt.open(srt_path, encoding="utf-8")
        print(f"📝 成功讀取字幕檔，共 {len(subs)} 筆字幕")
    except Exception as e:
        print(f"❌ 讀取字幕檔失敗：{e}")
        return False

    success_count = 0
    error_count = 0
    temp_files = []  # 追蹤暫存檔案

    for idx, sub in enumerate(subs, start=1):
        temp_file = None
        try:
            start = srt_time_to_seconds(sub.start)
            end = srt_time_to_seconds(sub.end)
            midpoint = (start + end) / 2

            output_file = os.path.join(output_dir, f"{idx:04d}.jpg")

            # 超強清理字幕文字
            original_text = sub.text.strip()
            clean_text = ultra_clean_subtitle_text(original_text)

            print(f"📸 處理第 {idx:04d} 張 @ {midpoint:.2f}s")
            print(f"   原始：{original_text[:30]}...")
            print(f"   清理：{clean_text}")

            # 建立暫存檔案
            temp_file = create_safe_subtitle_file(clean_text, idx)
            if temp_file:
                temp_files.append(temp_file)

                # 使用 textfile 參數
                drawtext_filter = (
                    f"drawtext="
                    f"fontfile='{selected_font}':"
                    f"textfile='{temp_file.replace(chr(92), '/')}':"
                    f"fontcolor=white:"
                    f"fontsize=28:"
                    f"borderw=2:"
                    f"bordercolor=black:"
                    f"x=(w-text_w)/2:"
                    f"y=h-50"
                )
            else:
                # 退回到最簡單的固定文字
                drawtext_filter = (
                    f"drawtext="
                    f"fontfile='{selected_font}':"
                    f"text='字幕 {idx:04d}':"
                    f"fontcolor=white:"
                    f"fontsize=28:"
                    f"borderw=2:"
                    f"bordercolor=black:"
                    f"x=(w-text_w)/2:"
                    f"y=h-50"
                )

            # 構建 FFmpeg 命令
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                f"{midpoint:.3f}",
                "-i",
                mp4_path,
                "-frames:v",
                "1",
                "-vf",
                drawtext_filter,
                "-q:v",
                "2",
                "-y",
                output_file,
            ]

            # 執行命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)

            if result.returncode == 0:
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    if file_size > 1000:  # 確保不是空檔案
                        print(f"   ✅ 成功 ({file_size} bytes)")
                        success_count += 1
                    else:
                        print(f"   ❌ 檔案太小 ({file_size} bytes)")
                        error_count += 1
                else:
                    print(f"   ❌ 檔案未生成")
                    error_count += 1
            else:
                print(f"   ❌ FFmpeg 錯誤 (返回碼: {result.returncode})")

                # 嘗試不加字幕的版本
                print(f"   🔄 嘗試無字幕版本...")
                fallback_cmd = [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-ss",
                    f"{midpoint:.3f}",
                    "-i",
                    mp4_path,
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    "-y",
                    output_file,
                ]

                fallback_result = subprocess.run(
                    fallback_cmd, capture_output=True, text=True, timeout=30
                )
                if fallback_result.returncode == 0 and os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"   ✅ 無字幕版本成功 ({file_size} bytes)")
                    success_count += 1
                else:
                    print(f"   ❌ 無字幕版本也失敗")
                    if result.stderr:
                        error_lines = [
                            line
                            for line in result.stderr.split("\n")
                            if "error" in line.lower()
                        ]
                        if error_lines:
                            print(f"   錯誤: {error_lines[0]}")
                    error_count += 1

        except subprocess.TimeoutExpired:
            print(f"   ❌ 處理超時")
            error_count += 1
        except Exception as e:
            print(f"   ❌ 異常：{e}")
            error_count += 1

        # 清理單個暫存檔
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

    # 清理所有暫存檔案
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass

    print(f"\n📊 處理完成！")
    print(f"✅ 成功：{success_count} 張")
    print(f"❌ 失敗：{error_count} 張")
    print(f"📈 成功率：{(success_count/(success_count+error_count)*100):.1f}%")

    if success_count > 0:
        print(f"📁 圖片已儲存至：{os.path.abspath(output_dir)}")
        return True
    else:
        print("\n🔧 故障排除建議：")
        print("1. 檢查 FFmpeg 版本是否過舊")
        print("2. 嘗試不同的字型檔案")
        print("3. 檢查字幕檔是否有編碼問題")
        return False


def main():
    print("🎬 強化版字幕截圖工具")
    print("=" * 40)

    mp4_path = input("📥 請輸入 MP4 路徑：").strip('" ')
    srt_path = input("📥 請輸入 SRT 路徑：").strip('" ')
    output_dir = input("📤 請輸入輸出資料夾（預設 output_images）：").strip('" ')

    if not output_dir:
        output_dir = "output_images"

    # 檢查檔案
    print("\n🔍 檢查檔案...")
    if not os.path.isfile(mp4_path):
        print(f"❌ MP4 路徑無效：{mp4_path}")
        return
    else:
        file_size = os.path.getsize(mp4_path) / 1024 / 1024
        print(f"✅ MP4 檔案存在：{file_size:.1f} MB")

    if not os.path.isfile(srt_path):
        print(f"❌ SRT 路徑無效：{srt_path}")
        return
    else:
        with open(srt_path, "r", encoding="utf-8") as f:
            first_lines = f.read(200)
            print(f"✅ SRT 檔案存在，內容預覽：{first_lines[:50]}...")

    # 開始處理
    print("\n🚀 開始強化處理...")
    success = extract_images_with_robust_subtitles(mp4_path, srt_path, output_dir)

    if success:
        print("\n🎉 處理完成！")
    else:
        print("\n😞 大部分處理失敗")


if __name__ == "__main__":
    main()
