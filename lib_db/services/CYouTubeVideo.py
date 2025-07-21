from yt_dlp import YoutubeDL
from typing import Optional, Dict, List
import requests
import os
import subprocess
from lib_db.services.CVideoManager import VideoManager


class YouTubeVideo:
    def __init__(
        self,
        url: str,
        srt_dir: str = "c:/ytdb/srt",
        thumbnail_dir: str = "c:/ytdb/thumbnails",
        video_path: str = "c:/ytdb/mp4",
        audio_path: str = "c:/ytdb/mp3",
    ):
        self.url = url
        self.info: Optional[Dict] = None
        self.srt_dir = srt_dir
        self.thumbnail_dir = thumbnail_dir
        self.video_path = video_path
        self.audio_path = audio_path

    # 使用 yt_dlp 的 extract_info 來取得影片完整的 metadata。 不下載影片，只取得 JSON 格式的資料。
    def fetch_info(self):
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            self.info = ydl.extract_info(self.url, download=False)

        return self.info

    # 顯示基本影片資訊，如標題、ID、上傳者、觀看次數、縮圖網址等 有處理影片長度的格式化（轉成 hh:mm:ss）。
    def print_info(self):
        if not self.info:
            self.fetch_info()

        print(f"影片標題: {self.info['title']}")
        print(f"影片ID: {self.info['id']}")
        print(f"上傳者: {self.info['uploader']}")
        print(f"上傳日期: {self.info['upload_date']}")
        print(f"觀看次數: {self.info['view_count']}")
        print(f"影片網址: {self.info['webpage_url']}")
        print(f"封面圖: {self.get_thumbnail_url()}")
        print(f"影片格式: {self.info['ext']}")
        print(f"影片類別: {self.info.get('category', '無')}")
        duration = self.info.get("duration")
        if duration:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            print(f"影片長度: {hours:02}:{minutes:02}:{seconds:02}（共 {duration} 秒）")
        else:
            print("影片長度: 無資料")

    # 回傳影片縮圖 URL，來自 info['thumbnail'] 欄位。
    def get_thumbnail_url(self):
        if not self.info:
            self.fetch_info()
        return self.info.get("thumbnail")

    # 下載整個影片，並儲存到指定目錄，檔名為影片 ID。
    def download(self):
        """下載影片到 srt_dir 指定資料夾"""
        if not os.path.exists(self.srt_dir):
            os.makedirs(self.srt_dir)

        # 用影片 ID 命名檔案
        ydl_opts = {
            "outtmpl": f"{self.srt_dir}/%(id)s.%(ext)s",  # 檔名使用影片 ID
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

    # 下載影片的縮圖並儲存成 影片ID.jpg。 使用 requests 下載圖片。
    def download_thumbnail(self):
        """下載縮圖到 thumbnail_dir 指定資料夾"""
        if not self.info:
            self.fetch_info()
        url = self.get_thumbnail_url()

        if not os.path.exists(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir)

        filename = f"{self.thumbnail_dir}/{self.info['id']}.jpg"
        with open(filename, "wb") as f:
            f.write(requests.get(url).content)
        print(f"已下載縮圖: {filename}")
        return filename

    # 回傳影片所有支援的字幕語言（手動 + 自動字幕的語言代碼）
    def get_available_subtitles(self) -> List[str]:
        """回傳該影片可用的字幕語言（代碼）"""
        if not self.info:
            self.fetch_info()

        subtitles = self.info.get("subtitles", {})
        automatic_captions = self.info.get("automatic_captions", {})

        # 合併手動字幕和自動字幕
        all_subtitles = {**subtitles, **automatic_captions}
        return list(all_subtitles.keys())

    # 從 YouTube 下載 .srt 字幕檔案。
    # 優先根據使用者提供的語言清單（例如：["en", "zh-TW"]）挑選合適語言。
    # 設定 writeautomaticsub 以便抓自動字幕（若沒手動的話）。
    def download_subtitle(self, preferred_langs: List[str] = None) -> str:
        """
        下載字幕到 self.srt_dir

        Args:
            preferred_langs: 偏好的語言列表，預設為 ['en', 'en-US', 'zh-TW', 'zh-CN']

        Returns:
            下載的字幕檔案路徑，若失敗則返回 None
        """
        if not self.info:
            self.fetch_info()

        if not os.path.exists(self.srt_dir):
            os.makedirs(self.srt_dir)

        # 預設偏好語言順序
        if preferred_langs is None:
            preferred_langs = ["en", "en-US", "zh-TW", "zh-CN", "zh"]

        available_langs = self.get_available_subtitles()
        print(f"可用字幕語言: {available_langs}")

        if not available_langs:
            print("此影片沒有字幕可下載")
            return None

        # 選擇語言：優先使用偏好語言，否則使用第一個可用語言
        selected_lang = None
        for lang in preferred_langs:
            if lang in available_langs:
                selected_lang = lang
                break

        if not selected_lang:
            selected_lang = available_langs[0]

        print(f"選擇下載語言: {selected_lang}")

        # 字幕檔案路徑
        subtitle_filename = f"{self.info['id']}.{selected_lang}.srt"
        subtitle_path = os.path.join(self.srt_dir, subtitle_filename)

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,  # 也下載自動字幕
            "subtitleslangs": [selected_lang],
            "subtitlesformat": "srt",
            "outtmpl": os.path.join(self.srt_dir, f"{self.info['id']}.%(ext)s"),
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            # 檢查檔案是否成功下載
            if os.path.exists(subtitle_path):
                print(f"字幕下載成功: {subtitle_path}")
                return subtitle_path
            else:
                # 嘗試尋找實際下載的檔案
                for file in os.listdir(self.srt_dir):
                    if file.startswith(self.info["id"]) and file.endswith(".srt"):
                        actual_path = os.path.join(self.srt_dir, file)
                        print(f"字幕下載成功: {actual_path}")
                        return actual_path

                print("字幕下載失敗：找不到下載的檔案")
                return None

        except Exception as e:
            print(f"字幕下載失敗: {str(e)}")
            return None

    # 將影片資訊轉為適合存入資料庫的 Dict 格式，欄位包括：id, title, uploader, upload_date, view_countvideo_url, thumbnail_url, local_thumbnail_path, format, duration
    def to_database_format(self, local_thumbnail_path: str = None) -> Dict:
        if not self.info:
            self.fetch_info()

        return {
            "id": self.info.get("id"),
            "title": self.info.get("title"),
            "uploader": self.info.get("uploader"),
            "upload_date": self.info.get("upload_date"),
            "view_count": self.info.get("view_count", 0),
            "video_url": self.info.get("webpage_url"),
            "thumbnail_url": self.get_thumbnail_url(),
            "local_thumbnail_path": local_thumbnail_path,
            "format": self.info.get("ext"),
            "duration": self.info.get("duration", 0),
        }

    # 使用 PostgreSQL VideoManager 保存資料
    def save_to_database(
        self, db_manager: VideoManager = None, download_thumbnail: bool = True
    ):
        """保存影片資料到 PostgreSQL 資料庫"""
        if not self.info:
            self.fetch_info()

        # 如果沒有提供 db_manager，建立一個新的
        if db_manager is None:
            db_manager = VideoManager()

        video_id = self.info.get("id")
        if db_manager.video_exists(video_id):
            print(f"影片 {video_id} 已存在於資料庫中")
            return video_id

        local_thumbnail_path = None
        if download_thumbnail:
            try:
                self.download_subtitle()
                local_thumbnail_path = self.download_thumbnail()
            except Exception as e:
                print(f"下載縮圖失敗: {e}")

        video_data = self.to_database_format(local_thumbnail_path)
        db_manager.add_or_update_video(video_data)

        print(f"影片 {video_id} 已成功儲存到資料庫")
        return video_id

    # 下載youtube檔案
    def download_video_with_audio(self) -> str | None:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "outtmpl": self.video_path,
            "merge_output_format": "mp4",
            "quiet": False,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                print("🎥 正在下載影片（含音訊）...")
                ydl.download([self.url])
                print(f"✅ 影片已下載：{self.video_path}")
                return self.video_path
        except Exception as e:
            print(f"❌ 影片下載錯誤：{e}")
            return None

    # 從 mp4 取出 mp3
    def extract_mp3_from_video(self) -> str | None:
        """
        從 MP4 影片中提取 MP3 音訊
        """
        if not os.path.exists(self.video_path):
            print("⚠️ 錯誤：影片檔案不存在，無法提取音訊。")
            return None

        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                self.video_path,
                "-vn",  # 不要影片
                "-acodec",
                "libmp3lame",
                "-ab",
                "192k",
                self.audio_path,
            ]
            print("🎧 正在提取 MP3 音訊...")
            subprocess.run(cmd, check=True)
            print(f"✅ 音訊已輸出為：{self.audio_path}")
            return self.audio_path
        except Exception as e:
            print(f"❌ 音訊提取失敗：{e}")
            return None
