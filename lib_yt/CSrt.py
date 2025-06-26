import yt_dlp
import os
import re
from datetime import datetime, timedelta


class SubtitleProcessor:
    @staticmethod
    def parse_srt_time(time_str):
        time_str = time_str.replace(",", ".")
        time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
        return timedelta(
            hours=time_obj.hour,
            minutes=time_obj.minute,
            seconds=time_obj.second,
            microseconds=time_obj.microsecond,
        )

    @staticmethod
    def format_srt_time(time_delta):
        total_seconds = int(time_delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = time_delta.microseconds // 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    @staticmethod
    def clean_content(content):
        content = re.sub(r"<[^>]+>", "", content)
        content = re.sub(r"\s+", " ", content).strip()
        content = re.sub(r"[.]{2,}", "...", content)
        content = re.sub(r"[?]{2,}", "?", content)
        content = re.sub(r"[!]{2,}", "!", content)
        return content

    def remove_duplicates(self, srt_content):
        blocks = re.split(r"\n\s*\n", srt_content.strip())
        cleaned = []
        prev_content = ""
        prev_end = None

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue
            try:
                index, time_line, *content_lines = lines
                match = re.match(
                    r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})",
                    time_line,
                )
                if not match:
                    continue
                start_str, end_str = match.groups()
                start = self.parse_srt_time(start_str)
                end = self.parse_srt_time(end_str)
                content = self.clean_content(" ".join(content_lines))
                if content == prev_content:
                    continue
                if prev_end and start < prev_end:
                    start = prev_end + timedelta(milliseconds=1)
                    if start >= end:
                        continue
                if (end - start).total_seconds() < 0.1:
                    continue
                new_block = f"{len(cleaned) + 1}\n{self.format_srt_time(start)} --> {self.format_srt_time(end)}\n{content}"
                cleaned.append(new_block)
                prev_content, prev_end = content, end
            except Exception as e:
                print(f"❌ 清理錯誤: {e}")
                continue
        return "\n\n".join(cleaned)

    def adjust_timing(self, srt_content, offset=0, speed=1.0):
        blocks = re.split(r"\n\s*\n", srt_content.strip())
        adjusted = []

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue
            try:
                idx, time_line, *content_lines = lines
                match = re.match(
                    r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})",
                    time_line,
                )
                if not match:
                    continue
                start, end = map(self.parse_srt_time, match.groups())
                start = timedelta(seconds=start.total_seconds() / speed + offset)
                end = timedelta(seconds=end.total_seconds() / speed + offset)
                start = max(start, timedelta(0))
                end = max(end, timedelta(0))
                adjusted.append(
                    f"{idx}\n{self.format_srt_time(start)} --> {self.format_srt_time(end)}\n"
                    + "\n".join(content_lines)
                )
            except Exception as e:
                print(f"❌ 時間調整錯誤: {e}")
                continue
        return "\n\n".join(adjusted)


class YouTubeSubtitleDownloader:
    def __init__(self, url, lang, folder="./subs"):
        self.url = url
        self.lang = lang
        self.folder = folder

    def download(self):
        os.makedirs(self.folder, exist_ok=True)
        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [self.lang],
            "subtitlesformat": "srt",
            "outtmpl": f"{self.folder}/%(title)s.%(ext)s",
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([self.url])

    @staticmethod
    def get_languages(url):
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "manual": list(info.get("subtitles", {}).keys()),
                "automatic": list(info.get("automatic_captions", {}).keys()),
            }


class SubtitleApp:
    def __init__(self):
        self.processor = SubtitleProcessor()

    def run(self):
        print("🎬 YouTube 字幕處理器")
        url = input("請輸入影片網址：").strip()
        if not url:
            print("❌ 無效網址")
            return

        lang = self.select_language(url)
        folder = input("輸出資料夾（Enter 使用預設 ./subs）：").strip() or "./subs"

        downloader = YouTubeSubtitleDownloader(url, lang, folder)
        print("📥 正在下載字幕...")
        downloader.download()

        for fname in os.listdir(folder):
            if not fname.endswith(".srt"):
                continue
            path = os.path.join(folder, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            print(f"🔍 處理字幕: {fname}")
            cleaned = self.processor.remove_duplicates(content)
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print("✅ 去重複完成")

    def select_language(self, url):
        langs = YouTubeSubtitleDownloader.get_languages(url)
        all_langs = sorted(set(langs["manual"]) | set(langs["automatic"]))
        print("\n可用語言：", ", ".join(all_langs))
        lang = input("請輸入語言代碼（例如 zh-Hant）：").strip()
        return lang


if __name__ == "__main__":
    app = SubtitleApp()
    app.run()
