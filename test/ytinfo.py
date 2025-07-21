# 取得 vedio info 資訊
from yt_dlp import YoutubeDL


def fetch_video_info(url: str):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,  # 不下載影片
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # 將所有資訊寫入檔案
    output_path = "C:/temp/ytinfo.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("🧾 所有影片資訊欄位:\n")
        for key, value in info.items():
            f.write(f"{key}: {value}\n")

    print(f"✅ 影片資訊已寫入 {output_path}")

    # 精選資訊仍顯示在終端機
    print("\n📌 精選影片資訊:")
    print("🎬 影片標題:", info.get("title"))
    print("📺 上傳者:", info.get("uploader"))
    print("📅 上傳日期:", info.get("upload_date"))
    print("👀 觀看次數:", info.get("view_count"))
    print("🎞 類別:", info.get("categories", "無"))
    print("🧩 格式:", info.get("ext"))
    print("🌐 網址:", info.get("webpage_url"))
    print("🖼 封面圖:", info.get("thumbnail"))
    print("⏱ 時長（秒）:", info.get("duration"))


# 測試用影片網址
youtube_url = "https://www.youtube.com/watch?v=FHJi8fuo_E4&ab_channel=BBCNews"
fetch_video_info(youtube_url)
