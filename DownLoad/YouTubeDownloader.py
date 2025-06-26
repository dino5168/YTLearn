import yt_dlp
from datetime import datetime


class YouTubeAudioDownloader:
    def __init__(self, url: str, output_filename: str = None, keep_video: bool = True):
        """
        初始化下載器

        :param url: YouTube 影片網址
        :param output_filename: 輸出檔名（不含副檔名）
        :param keep_video: 是否保留原始影片檔
        """
        self.url = url
        self.output_filename = output_filename or self._generate_default_filename()
        self.keep_video = keep_video

    def _generate_default_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"youtube_audio_{timestamp}"

    def download(self) -> str | None:
        """
        執行音訊下載與轉檔為 MP3

        :return: 成功時回傳 mp3 檔案路徑，失敗時回傳 None
        """
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{self.output_filename}.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "keepvideo": self.keep_video,
            "quiet": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("🔽 正在下載並轉換為 MP3...")
                ydl.download([self.url])
                print(f"✅ 音訊已儲存為：{self.output_filename}.mp3")
                return f"{self.output_filename}.mp3"
        except Exception as e:
            print(f"❌ 下載錯誤：{e}")
            return None


# 測試用例
if __name__ == "__main__":
    video_url = input("請輸入 YouTube 影片網址：").strip()
    output_name = input("請輸入輸出檔案名稱（可留空使用預設）：").strip() or None

    downloader = YouTubeAudioDownloader(url=video_url, output_filename=output_name)
    result = downloader.download()

    if result:
        print("🎉 下載完成！")
    else:
        print("⚠️ 下載失敗，請確認網址是否正確。")
