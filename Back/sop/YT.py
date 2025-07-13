import yt_dlp
import os


def ensure_output_dir(path="C:/temp"):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def download_video(url, output_path):
    """下載影片，嘗試多種格式選項"""
    format_options = [
        "bestvideo[height<=720]+bestaudio",
        "bestvideo+bestaudio",
        "best",
        "worst",
    ]

    for i, format_option in enumerate(format_options):
        print(f"\n嘗試格式選項 {i+1}: {format_option}")

        ydl_opts = {
            "format": format_option,
            "outtmpl": os.path.join(output_path, "my_video.%(ext)s"),
            "no_warnings": False,
            "quiet": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("正在取得影片資訊...")
                info = ydl.extract_info(url, download=False)
                print(f"影片標題: {info.get('title', '未知')}")
                print(f"影片長度: {info.get('duration', '未知')} 秒")

                print("正在下載...")
                ydl.download([url])
                print("✅ 下載完成！")
                return True

        except Exception as e:
            print(f"❌ 格式選項 {i+1} 失敗: {str(e)}")
            continue

    print("所有格式選項都失敗了")
    return False


def main():
    print("=" * 50)
    print("🎬 YouTube 影片下載器")
    print("=" * 50)

    url = input("請輸入 YouTube 影片網址：").strip()
    if not url:
        print("❗ 請提供有效的網址")
        return

    output_path = ensure_output_dir()
    success = download_video(url, output_path)

    if not success:
        print("\n🚑 建議解決方案：")
        print("1. 更新 yt-dlp：pip install --upgrade yt-dlp")
        print("2. 檢查影片是否為私人或受限制")
        print("3. 嘗試不同的影片網址")
        print("4. 使用指令行：yt-dlp 'URL'")


if __name__ == "__main__":
    main()
