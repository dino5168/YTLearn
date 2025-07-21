import re
import os
import sys
import requests
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass


@dataclass
class YTInfo:
    id: str
    title: str
    uploader: str
    upload_date: str
    view_count: int
    category: str
    ext: str
    webpage_url: str
    thumbnail: str
    duration: int
    user_id: int
    lan: str


class YouTubeHandler:
    def __init__(self, url: str, output_dir: str = "C:/temp"):
        self.url = url
        self.output_dir = output_dir
        # 確保輸出資料夾存在
        os.makedirs(self.output_dir, exist_ok=True)
        self.ytinfo = None

    def sanitize_directory_name(self, name: str) -> str:
        # 將 &、空格、- 等符號轉換為底線
        name = re.sub(r"[&\s\-]+", "_", name)
        # 移除所有非英數字和底線
        name = re.sub(r"[^\w]", "", name)
        # 移除開頭或結尾多餘底線
        name = name.strip("_")
        return name.lower()

    def extract_video_id(self) -> str:
        """從 YouTube URL 擷取影片 ID"""
        parsed_url = urlparse(self.url)

        # 處理不同的 YouTube URL 格式
        if parsed_url.hostname in ["youtu.be"]:
            return parsed_url.path[1:]
        elif parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            query = parse_qs(parsed_url.query)
            return query.get("v", [""])[0]
        else:
            return ""

    def fetch_video_info(self) -> YTInfo:
        """擷取影片資訊"""
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }

        video_id = self.extract_video_id()

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            # 安全地取得分類資訊
            categories = info.get("categories", [])
            category = categories[0] if categories else "無分類"
            category = self.sanitize_directory_name(category)  # 正規化目錄字串

            ytinfo = YTInfo(
                id=video_id,
                title=info.get("title", "無標題"),
                uploader=info.get("uploader", "無上傳者"),
                upload_date=info.get("upload_date", "無日期"),
                view_count=info.get("view_count", 0) or 0,
                category=category,
                ext=info.get("ext", "無格式"),
                webpage_url=info.get("webpage_url", ""),
                thumbnail=info.get("thumbnail", ""),
                duration=info.get("duration", 0) or 0,
            )

            # 顯示影片資訊
            self.output_dir = os.path.join(self.output_dir, ytinfo.category, ytinfo.id)
            print("建立目錄")
            os.makedirs(self.output_dir, exist_ok=True)  # 建立目錄
            self._display_video_info(ytinfo)
            return ytinfo

        except Exception as e:
            print(f"❌ 取得影片資訊時發生錯誤: {e}")
            raise

    def _display_video_info(self, ytinfo: YTInfo):
        """顯示影片資訊"""
        print("\n📌 精選影片資訊:")
        print("🆔 影片 ID:", ytinfo.id)
        print("🎬 影片標題:", ytinfo.title)
        print("📺 上傳者:", ytinfo.uploader)
        print("📅 上傳日期:", ytinfo.upload_date)
        print(
            "👀 觀看次數:", f"{ytinfo.view_count:,}" if ytinfo.view_count else "無資料"
        )
        print("🎞 類別:", ytinfo.category)
        print("🧩 格式:", ytinfo.ext)
        print("🌐 網址:", ytinfo.webpage_url)
        print("🖼 封面圖:", ytinfo.thumbnail)
        print("⏱ 時長（秒）:", ytinfo.duration)
        print("⏱ 時長（分:秒）:", f"{ytinfo.duration // 60}:{ytinfo.duration % 60:02d}")

    def download_audio(self, use_video_id: bool = True) -> str:
        """下載音訊為 MP3 格式"""
        video_id = self.extract_video_id()

        if use_video_id and video_id:
            output_filename = f"{video_id}.mp3"
        else:
            output_filename = "audio.mp3"

        output_path = os.path.join(self.output_dir, output_filename)
        print("下載音訊為 MP3 格式")
        print(output_path)

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": os.path.join(self.output_dir, f"temp_{video_id}.%(ext)s"),
            "quiet": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)

            # 找出實際的下載檔案
            temp_files = [
                f
                for f in os.listdir(self.output_dir)
                if f.startswith(f"temp_{video_id}") and f.endswith(".mp3")
            ]

            if temp_files:
                temp_path = os.path.join(self.output_dir, temp_files[0])
                # 重新命名為指定檔案名
                if os.path.exists(temp_path):
                    os.rename(temp_path, output_path)
                    print(f"✅ 音訊已下載並儲存為：{output_path}")
                    return output_path

            print("❌ 無法找到下載的音訊檔案")
            return ""

        except Exception as e:
            print(f"❌ 下載音訊時發生錯誤: {e}")
            raise

    def download_thumbnail(self, use_video_id: bool = True) -> str:
        """下載封面圖片"""
        video_id = self.extract_video_id()

        try:
            # 先取得影片資訊以獲得縮圖 URL
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            thumbnail_url = info.get("thumbnail", "")
            if not thumbnail_url:
                print("❌ 無法取得封面圖片網址")
                return ""

            # 判斷圖片格式
            if any(ext in thumbnail_url.lower() for ext in [".jpg", "jpg"]):
                img_ext = "jpg"
            elif any(ext in thumbnail_url.lower() for ext in [".jpeg", "jpeg"]):
                img_ext = "jpeg"
            elif any(ext in thumbnail_url.lower() for ext in [".png", "png"]):
                img_ext = "png"
            elif any(ext in thumbnail_url.lower() for ext in [".webp", "webp"]):
                img_ext = "jpg"  # WebP 轉為 JPG
            else:
                img_ext = "jpg"  # 預設為 JPG

            # 設定輸出檔名
            if use_video_id and video_id:
                output_filename = f"{video_id}.{img_ext}"
            else:
                output_filename = f"thumbnail.{img_ext}"

            output_path = os.path.join(self.output_dir, output_filename)

            # 下載圖片
            print(f"🖼 正在下載封面圖片...")
            response = requests.get(thumbnail_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✅ 封面圖片已下載並儲存為：{output_path}")
            return output_path

        except requests.RequestException as e:
            print(f"❌ 下載封面圖片時發生網路錯誤: {e}")
            return ""
        except Exception as e:
            print(f"❌ 下載封面圖片時發生錯誤: {e}")
            return ""

    def process_video(
        self, download_audio: bool = True, download_thumbnail: bool = True
    ) -> tuple[YTInfo, str, str]:
        """完整處理流程：取得資訊 + 下載音訊 + 下載封面"""
        print("🚀 開始處理 YouTube 影片...")

        # 1. 取得影片資訊
        video_info = self.fetch_video_info()

        audio_path = ""
        thumbnail_path = ""

        if download_audio:
            print("\n🎵 開始下載音訊...")
            audio_path = self.download_audio()

        if download_thumbnail:
            print("\n🖼 開始下載封面...")
            thumbnail_path = self.download_thumbnail()

        print("\n🎉 處理完成！")
        return video_info, audio_path, thumbnail_path


# 使用範例
if __name__ == "__main__":
    # 使用範例
    url = input("請輸入 YouTube 影片網址: ")
    output_dir = input("請輸入儲存資料夾路徑 (預設 C:/temp): ") or "C:/temp"

    try:
        handler = YouTubeHandler(url, output_dir)

        # 方法1: 分別執行
        # video_info = handler.fetch_video_info()
        # audio_path = handler.download_audio()
        # thumbnail_path = handler.download_thumbnail()

        # 方法2: 一次性處理
        video_info, audio_path, thumbnail_path = handler.process_video()

        print(f"\n✨ 處理結果:")
        print(f"📄 影片資訊: {video_info.title}")
        print(f"🎵 音訊檔案: {audio_path}")
        print(f"🖼 封面圖片: {thumbnail_path}")

    except Exception as e:
        print(f"💥 發生錯誤: {e}")
