import yt_dlp
import os
import re
from datetime import datetime, timedelta


def parse_srt_time(time_str):
    """解析 SRT 時間格式"""
    time_str = time_str.replace(",", ".")
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    return timedelta(
        hours=time_obj.hour,
        minutes=time_obj.minute,
        seconds=time_obj.second,
        microseconds=time_obj.microsecond,
    )


def format_srt_time(time_delta):
    """格式化時間為 SRT 格式"""
    total_seconds = int(time_delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = time_delta.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def clean_subtitle_content(content):
    """清理字幕內容，移除重複和無用標籤"""
    # 移除 HTML 標籤
    content = re.sub(r"<[^>]+>", "", content)

    # 移除多餘空白
    content = re.sub(r"\s+", " ", content).strip()

    # 移除重複的標點符號
    content = re.sub(r"[.]{2,}", "...", content)
    content = re.sub(r"[?]{2,}", "?", content)
    content = re.sub(r"[!]{2,}", "!", content)

    return content


def remove_duplicate_subtitles(srt_content):
    """移除重複的字幕條目"""
    # 解析 SRT 內容
    subtitle_blocks = re.split(r"\n\s*\n", srt_content.strip())
    cleaned_subtitles = []
    previous_content = ""
    previous_end_time = None

    for block in subtitle_blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        try:
            # 解析字幕編號、時間和內容
            subtitle_id = lines[0]
            time_line = lines[1]
            content_lines = lines[2:]

            # 解析時間
            time_match = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line
            )
            if not time_match:
                continue

            start_time_str, end_time_str = time_match.groups()
            start_time = parse_srt_time(start_time_str)
            end_time = parse_srt_time(end_time_str)

            # 清理內容
            content = " ".join(content_lines)
            content = clean_subtitle_content(content)

            # 檢查是否為重複內容
            if content == previous_content:
                # 如果內容相同，跳過
                continue

            # 檢查時間重疊
            if previous_end_time and start_time < previous_end_time:
                # 調整開始時間以避免重疊
                start_time = previous_end_time + timedelta(milliseconds=1)
                if start_time >= end_time:
                    continue

            # 檢查字幕長度是否合理
            duration = end_time - start_time
            if duration.total_seconds() < 0.1:  # 少於0.1秒的字幕可能有問題
                continue

            # 重新格式化時間
            start_time_str = format_srt_time(start_time)
            end_time_str = format_srt_time(end_time)

            # 建立清理後的字幕塊
            cleaned_block = f"{len(cleaned_subtitles) + 1}\n{start_time_str} --> {end_time_str}\n{content}"
            cleaned_subtitles.append(cleaned_block)

            previous_content = content
            previous_end_time = end_time

        except Exception as e:
            print(f"處理字幕塊時出錯: {e}")
            continue

    return "\n\n".join(cleaned_subtitles)


def post_process_subtitles(output_folder):
    """後處理字幕檔案，移除重複"""
    srt_files = [f for f in os.listdir(output_folder) if f.endswith(".srt")]

    for srt_file in srt_files:
        file_path = os.path.join(output_folder, srt_file)
        print(f"正在清理字幕檔案: {srt_file}")

        try:
            # 讀取原始檔案
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # 清理重複
            cleaned_content = remove_duplicate_subtitles(original_content)

            # 備份原始檔案
            backup_path = file_path.replace(".srt", "_original.srt")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(original_content)

            # 寫入清理後的內容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)

            print(f"✅ 字幕清理完成: {srt_file}")
            print(f"📁 原始檔案備份為: {os.path.basename(backup_path)}")

        except Exception as e:
            print(f"❌ 清理字幕檔案 {srt_file} 時出錯: {e}")


def get_available_languages(url: str):
    """
    獲取影片可用的字幕語言
    """
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # 獲取手動字幕和自動字幕
            manual_subs = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {})

            all_langs = set(manual_subs.keys()) | set(auto_subs.keys())

            return {
                "manual": list(manual_subs.keys()),
                "automatic": list(auto_subs.keys()),
                "all": sorted(list(all_langs)),
            }
    except Exception as e:
        print(f"無法獲取字幕資訊：{e}")
        return None


def download_youtube_subtitles(
    url: str,
    lang: str = "zh-Hant",
    output_folder: str = "./subs",
    clean_duplicates: bool = True,
):
    """
    下載 YouTube 字幕（轉錄稿）為 srt 格式

    :param url: YouTube 影片網址
    :param lang: 語言代碼
    :param output_folder: 儲存資料夾
    :param clean_duplicates: 是否清理重複字幕
    """
    # 確保輸出資料夾存在
    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang],
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
        "subtitlesformat": "srt",
        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ 字幕下載完成！語言：{lang}")

        # 後處理：清理重複字幕
        if clean_duplicates:
            print("\n🔧 開始清理重複字幕...")
            post_process_subtitles(output_folder)

    except Exception as e:
        print(f"❌ 下載失敗：{e}")


def display_language_options():
    """
    顯示常用語言選項
    """
    common_languages = {
        "1": ("zh-Hant", "繁體中文"),
        "2": ("zh-Hans", "簡體中文"),
        "3": ("en", "英文"),
        "4": ("ja", "日文"),
        "5": ("ko", "韓文"),
        "6": ("es", "西班牙文"),
        "7": ("fr", "法文"),
        "8": ("de", "德文"),
        "9": ("pt", "葡萄牙文"),
        "10": ("ru", "俄文"),
    }

    print("\n=== 常用語言選項 ===")
    for key, (code, name) in common_languages.items():
        print(f"{key}. {name} ({code})")
    print("11. 查看影片所有可用語言")
    print("12. 手動輸入語言代碼")

    return common_languages


def select_language(url: str):
    """
    讓使用者選擇語言
    """
    common_languages = display_language_options()

    while True:
        choice = input("\n請選擇語言 (輸入數字): ").strip()

        if choice in common_languages:
            lang_code, lang_name = common_languages[choice]
            print(f"已選擇：{lang_name} ({lang_code})")
            return lang_code

        elif choice == "11":
            print("\n正在獲取影片可用語言...")
            langs_info = get_available_languages(url)

            if langs_info:
                print(f"\n=== 影片可用語言 ===")
                print(
                    f"手動字幕：{', '.join(langs_info['manual']) if langs_info['manual'] else '無'}"
                )
                print(
                    f"自動字幕：{', '.join(langs_info['automatic']) if langs_info['automatic'] else '無'}"
                )
                print(f"所有可用語言：{', '.join(langs_info['all'])}")

                lang_input = input("\n請輸入想要的語言代碼：").strip()
                if lang_input in langs_info["all"]:
                    return lang_input
                else:
                    print("❌ 該語言不可用！")
            else:
                print("❌ 無法獲取語言資訊")

        elif choice == "12":
            lang_input = input("請輸入語言代碼 (例如：zh-Hant): ").strip()
            if lang_input:
                return lang_input
            else:
                print("❌ 語言代碼不能為空！")

        else:
            print("❌ 請輸入有效的選項數字！")


def adjust_subtitle_timing(srt_content, offset_seconds=0, speed_ratio=1.0):
    """
    調整字幕時間軸

    :param srt_content: SRT 字幕內容
    :param offset_seconds: 時間偏移（秒），正數為延後，負數為提前
    :param speed_ratio: 速度比例，>1 為加速，<1 為減速
    """
    subtitle_blocks = re.split(r"\n\s*\n", srt_content.strip())
    adjusted_subtitles = []

    for block in subtitle_blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        try:
            subtitle_id = lines[0]
            time_line = lines[1]
            content_lines = lines[2:]

            # 解析時間
            time_match = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line
            )
            if not time_match:
                continue

            start_time_str, end_time_str = time_match.groups()
            start_time = parse_srt_time(start_time_str)
            end_time = parse_srt_time(end_time_str)

            # 應用速度調整
            start_time = timedelta(seconds=start_time.total_seconds() / speed_ratio)
            end_time = timedelta(seconds=end_time.total_seconds() / speed_ratio)

            # 應用時間偏移
            offset_delta = timedelta(seconds=offset_seconds)
            start_time += offset_delta
            end_time += offset_delta

            # 確保時間不為負數
            if start_time.total_seconds() < 0:
                start_time = timedelta(0)
            if end_time.total_seconds() < 0:
                end_time = timedelta(0)

            # 格式化時間
            start_time_str = format_srt_time(start_time)
            end_time_str = format_srt_time(end_time)

            # 重建字幕塊
            content = "\n".join(content_lines)
            adjusted_block = (
                f"{subtitle_id}\n{start_time_str} --> {end_time_str}\n{content}"
            )
            adjusted_subtitles.append(adjusted_block)

        except Exception as e:
            print(f"調整時間軸時出錯: {e}")
            continue

    return "\n\n".join(adjusted_subtitles)


def sync_subtitles_with_audio(output_folder):
    """
    同步字幕與音頻時間軸
    """
    srt_files = [
        f
        for f in os.listdir(output_folder)
        if f.endswith(".srt") and not f.endswith("_original.srt")
    ]

    if not srt_files:
        print("❌ 沒有找到字幕檔案")
        return

    print(f"\n🔧 找到 {len(srt_files)} 個字幕檔案")

    for srt_file in srt_files:
        print(f"\n正在處理: {srt_file}")

        # 詢問是否需要調整此檔案
        adjust = input(f"是否需要調整 {srt_file} 的時間軸？(y/N): ").strip().lower()
        if adjust != "y":
            continue

        file_path = os.path.join(output_folder, srt_file)

        try:
            # 讀取字幕檔案
            with open(file_path, "r", encoding="utf-8") as f:
                srt_content = f.read()

            # 獲取調整參數
            print("\n=== 時間軸調整選項 ===")
            print("1. 字幕比音頻慢 (字幕延後顯示)")
            print("2. 字幕比音頻快 (字幕提前顯示)")
            print("3. 字幕播放速度不對")
            print("4. 自訂調整")

            adjustment_type = input("請選擇調整類型 (1-4): ").strip()

            offset_seconds = 0
            speed_ratio = 1.0

            if adjustment_type == "1":
                # 字幕慢，需要提前
                seconds = float(input("字幕慢了幾秒？(輸入正數): "))
                offset_seconds = -seconds

            elif adjustment_type == "2":
                # 字幕快，需要延後
                seconds = float(input("字幕快了幾秒？(輸入正數): "))
                offset_seconds = seconds

            elif adjustment_type == "3":
                # 速度調整
                print("速度調整範例:")
                print("- 字幕播放太快: 輸入 0.9 (減速)")
                print("- 字幕播放太慢: 輸入 1.1 (加速)")
                speed_ratio = float(input("輸入速度比例: "))

            elif adjustment_type == "4":
                # 自訂
                offset_seconds = float(input("時間偏移（秒，正數=延後，負數=提前）: "))
                speed_ratio = float(input("速度比例（1.0=正常，>1=加速，<1=減速）: "))

            else:
                print("❌ 無效選項")
                continue

            # 執行調整
            adjusted_content = adjust_subtitle_timing(
                srt_content, offset_seconds, speed_ratio
            )

            # 建立調整後的檔案名稱
            name_parts = srt_file.rsplit(".", 1)
            adjusted_filename = f"{name_parts[0]}_adjusted.srt"
            adjusted_path = os.path.join(output_folder, adjusted_filename)

            # 寫入調整後的字幕
            with open(adjusted_path, "w", encoding="utf-8") as f:
                f.write(adjusted_content)

            print(f"✅ 時間軸調整完成")
            print(f"📁 調整後檔案: {adjusted_filename}")
            print(f"⏰ 時間偏移: {offset_seconds}秒")
            print(f"🏃 速度比例: {speed_ratio}")

        except Exception as e:
            print(f"❌ 調整時間軸失敗: {e}")


def main():
    """
    主程式
    """
    print("🎬 YouTube 字幕下載器 (含去重複功能)")
    print("=" * 40)

    # 獲取 YouTube 網址
    youtube_url = input("請輸入 YouTube 影片網址：").strip()

    if not youtube_url:
        print("❌ 網址不能為空！")
        return

    # 選擇語言
    selected_lang = select_language(youtube_url)

    # 選擇輸出資料夾
    output_folder = input("請輸入儲存資料夾路徑 (按 Enter 使用預設 ./subs)：").strip()
    if not output_folder:
        output_folder = "./subs"

    # 詢問是否清理重複
    clean_option = input("是否自動清理重複字幕？(Y/n)：").strip().lower()
    clean_duplicates = clean_option != "n"

    print(f"\n開始下載字幕...")
    print(f"網址：{youtube_url}")
    print(f"語言：{selected_lang}")
    print(f"儲存位置：{output_folder}")
    print(f"清理重複：{'是' if clean_duplicates else '否'}")
    print("-" * 50)

    # 下載字幕
    download_youtube_subtitles(
        youtube_url, selected_lang, output_folder, clean_duplicates
    )

    # 詢問是否需要調整時間軸
    sync_option = input("\n是否需要調整字幕時間軸？(y/N): ").strip().lower()
    if sync_option == "y":
        sync_subtitles_with_audio(output_folder)


# === 使用範例 ===
if __name__ == "__main__":
    main()
