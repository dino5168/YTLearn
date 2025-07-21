from dataclasses import dataclass
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs


@dataclass
class YTInfo:
    video_id: str
    title: str
    uploader: str
    upload_date: str
    view_count: int
    category: str
    ext: str
    webpage_url: str
    thumbnail: str
    duration: int


class YouTubeHandler:
    def __init__(self, output_dir: str = "C:/temp"):
        self.output_dir = output_dir

    def extract_video_id(self, url: str) -> str:
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        return query.get("v", [""])[0]

    def fetch_video_info(self, url: str) -> YTInfo:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }

        video_id = self.extract_video_id(url)

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        ytinfo = YTInfo(
            video_id=video_id,
            title=info.get("title", ""),
            uploader=info.get("uploader", ""),
            upload_date=info.get("upload_date", ""),
            view_count=info.get("view_count", 0),
            category=info.get("categories", [])[0] or "無",
            ext=info.get("ext", ""),
            webpage_url=info.get("webpage_url", ""),
            thumbnail=info.get("thumbnail", ""),
            duration=info.get("duration", 0),
        )

        print("\n📌 精選影片資訊:")
        print("🎬 影片標題:", ytinfo.video_id)
        print("🎬 影片標題:", ytinfo.title)
        print("📺 上傳者:", ytinfo.uploader)
        print("📅 上傳日期:", ytinfo.upload_date)
        print("👀 觀看次數:", ytinfo.view_count)
        print("🎞 類別:", ytinfo.category)
        print("🧩 格式:", ytinfo.ext)
        print("🌐 網址:", ytinfo.webpage_url)
        print("🖼 封面圖:", ytinfo.thumbnail)
        print("⏱ 時長（秒）:", ytinfo.duration)

        return ytinfo

    # 下載 mp3
    def download_audio(self, url: str):
        ydl_opts = {
            "format": "bestaudio",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": f"{self.output_dir}/%(title)s.%(ext)s",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ 音訊已下載完成")


# 使用範例
if __name__ == "__main__":
    handler = YouTubeHandler()
    url = "https://www.youtube.com/watch?v=jKi2SvWOCXc&ab_channel=TheFableCottage"

    video_id = handler.extract_video_id(url)
    print(f"🎯 Video ID: {video_id}")

    ytinfo = handler.fetch_video_info(url)
    # handler.download_audio(url)
