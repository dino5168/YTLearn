import requests


def download_youtube_thumbnail(video_id: str, filename: str = "thumbnail.jpg"):
    # 嘗試最高畫質封面
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
    ]

    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ 已下載封面: {url}")
            return
        else:
            print(f"❌ 封面不存在: {url}")

    print("⚠️ 找不到可用的封面圖。")


# 範例影片 ID（例如：https://www.youtube.com/watch?v=dQw4w9WgXcQ）
download_youtube_thumbnail("BboNahlElB8")
