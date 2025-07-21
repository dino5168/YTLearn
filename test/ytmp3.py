from yt_dlp import YoutubeDL


def download_audio(url: str):
    ydl_opts = {
        "format": "bestaudio",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",  # 可改成 m4a、opus...
                "preferredquality": "192",
            }
        ],
        "outtmpl": "C:/temp/%(title)s.%(ext)s",  # 儲存路徑格式
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# 測試
download_audio("https://www.youtube.com/watch?v=jKi2SvWOCXc&ab_channel=TheFableCottage")
