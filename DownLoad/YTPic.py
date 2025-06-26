import yt_dlp
import requests
import os


def get_video_id_from_url(url: str) -> str:
    """用 yt_dlp 提取 YouTube 影片 ID"""
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info.get("id", "")
        except Exception as e:
            print(f"❌ 取得影片 ID 時發生錯誤：{e}")
            return ""


def download_youtube_thumbnail(
    video_id: str, filename="thumbnail.jpg", resolution="maxresdefault"
):
    """根據影片 ID 下載封面圖片"""
    url = f"https://img.youtube.com/vi/{video_id}/{resolution}.jpg"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ 成功下載封面：{filename}")
        else:
            print(f"⚠️ 封面解析度 {resolution} 不存在，嘗試使用 hqdefault")
            if resolution != "hqdefault":
                download_youtube_thumbnail(video_id, filename, resolution="hqdefault")
    except Exception as e:
        print(f"❌ 下載圖片失敗：{e}")


def main():
    url = input("請輸入 YouTube 網址：").strip()
    if not url:
        print("❌ 沒有輸入網址")
        return

    video_id = get_video_id_from_url(url)
    if not video_id:
        print("❌ 無法取得影片 ID")
        return

    filename = f"{video_id}_thumbnail.jpg"
    download_youtube_thumbnail(video_id, filename)


if __name__ == "__main__":
    main()
