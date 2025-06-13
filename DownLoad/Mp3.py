import yt_dlp


def download_youtube_audio_mp3(url: str, output_folder: str = "./downloads"):
    """
    下載 YouTube 音訊並轉成 MP3 格式。

    :param url: YouTube 影片網址
    :param output_folder: 儲存資料夾（預設是 ./downloads）
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# === 使用範例 ===
if __name__ == "__main__":
    youtube_url = input("請輸入 YouTube 影片網址：")
    download_youtube_audio_mp3(youtube_url)
