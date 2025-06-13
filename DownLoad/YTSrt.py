import yt_dlp
import os


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
    url: str, lang: str = "zh-Hant", output_folder: str = "./subs"
):
    """
    下載 YouTube 字幕（轉錄稿）為 srt 格式

    :param url: YouTube 影片網址
    :param lang: 語言代碼
    :param output_folder: 儲存資料夾
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


def main():
    """
    主程式
    """
    print("🎬 YouTube 字幕下載器")
    print("=" * 30)

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

    print(f"\n開始下載字幕...")
    print(f"網址：{youtube_url}")
    print(f"語言：{selected_lang}")
    print(f"儲存位置：{output_folder}")
    print("-" * 50)

    # 下載字幕
    download_youtube_subtitles(youtube_url, selected_lang, output_folder)


# === 使用範例 ===
if __name__ == "__main__":
    main()
