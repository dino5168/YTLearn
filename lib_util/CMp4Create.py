from pathlib import Path
from typing import Dict
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import re
import traceback


class DualSubtitleVideoGenerator:
    """雙語字幕影片生成器"""

    def __init__(
        self,
        video_size=(1280, 720),
        fontsize=40,
        text_color=(255, 255, 255),
        bg_color=(0, 0, 0),
        subtitle_bottom_margin=80,
    ):
        """
        初始化生成器

        Args:
            video_size: 影片尺寸 (寬, 高)
            fontsize: 字體大小
            text_color: 文字顏色 (R, G, B)
            bg_color: 背景顏色 (R, G, B)
            subtitle_bottom_margin: 字幕距離底部的距離
        """
        self.video_size = video_size
        self.fontsize = fontsize
        self.text_color = text_color
        self.bg_color = bg_color
        self.subtitle_bottom_margin = subtitle_bottom_margin

        # 字型路徑設定
        self.en_font_paths = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ]

        self.zh_font_paths = [
            r"C:\Mp3\Test\BpmfGenSenRounded-B.ttf",
            r"C:\Windows\Fonts\msjh.ttc",
            r"C:\Windows\Fonts\simsun.ttc",
            r"C:\Windows\Fonts\mingliu.ttc",
        ]

        # 內部變數
        self.audio = None
        self.video = None
        self.background_image = None
        self.zh_subtitles = []
        self.merged_subtitles = []

    def parse_srt_time(self, time_str):
        """解析 SRT 時間格式 (HH:MM:SS,mmm)"""
        try:
            time_part, ms_part = time_str.split(",")
            h, m, s = map(int, time_part.split(":"))
            ms = int(ms_part)
            return h * 3600 + m * 60 + s + ms / 1000.0
        except:
            return 0

    def parse_srt_content(self, content):
        """解析 SRT 內容"""
        subtitles = []
        blocks = re.split(r"\n\s*\n", content.strip())

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                # 第一行是序號
                # 第二行是時間
                time_line = lines[1]
                time_match = re.search(
                    r"(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)", time_line
                )

                if time_match:
                    start_time = self.parse_srt_time(time_match.group(1))
                    end_time = self.parse_srt_time(time_match.group(2))
                    text = "\n".join(lines[2:])
                    subtitles.append((start_time, end_time, text))

        return subtitles

    def parse_subtitle_file(self, file_path):
        """解析字幕檔案"""
        try:
            # 嘗試不同編碼
            encodings = ["utf-8", "utf-8-sig", "big5", "gbk", "cp950"]
            content = None

            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                    print(f"成功使用 {encoding} 編碼讀取 {file_path}")
                    break
                except:
                    continue

            if not content:
                raise Exception("無法讀取檔案")

            # 檢查是否為 SRT 格式
            if re.search(r"\d+:\d+:\d+,\d+\s*-->\s*\d+:\d+:\d+,\d+", content):
                return self.parse_srt_content(content)
            else:
                # 普通文字檔案
                return [(0, None, content.strip())]

        except Exception as e:
            print(f"讀取檔案錯誤 {file_path}: {e}")
            return []

    def wrap_text(self, text, font, max_width, is_chinese=False):
        """根據字型和最大寬度自動換行，中英文分開處理"""
        lines = []
        current_line = ""
        temp_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(temp_img)

        if is_chinese:
            # 中文逐字處理（無空格）
            for char in text:
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                if width <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
        else:
            # 英文按單字處理（避免單字被切斷）
            words = text.split()
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                if width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

        return lines

    def load_fonts(self):
        """載入字型"""
        en_font = None
        zh_font = None

        try:
            # 載入英文字型
            for font_path in self.en_font_paths:
                if os.path.exists(font_path):
                    en_font = ImageFont.truetype(font_path, self.fontsize)
                    break

            # 載入中文字型
            for font_path in self.zh_font_paths:
                if os.path.exists(font_path):
                    zh_font = ImageFont.truetype(font_path, self.fontsize)
                    break

            if en_font is None:
                en_font = ImageFont.load_default()
            if zh_font is None:
                zh_font = ImageFont.load_default()

        except:
            en_font = ImageFont.load_default()
            zh_font = ImageFont.load_default()

        return en_font, zh_font

    def load_background_image(self, image_file):
        """載入背景圖片"""
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"找不到圖片檔案 {image_file}")

        print("載入背景圖片...")
        img = Image.open(image_file)

        # 調整圖片大小到指定尺寸
        img = img.resize(self.video_size, Image.Resampling.LANCZOS)

        # 轉換為 RGB 模式（以防是 RGBA 或其他模式）
        if img.mode != "RGB":
            img = img.convert("RGB")

        self.background_image = np.array(img)
        print(f"背景圖片已載入，尺寸: {self.video_size}")

    def create_text_image_with_background(self, zh_text):
        """建立帶背景圖片的中文字幕圖片"""
        # 使用背景圖片或純色背景
        if self.background_image is not None:
            img = Image.fromarray(self.background_image.copy())
        else:
            img = Image.new("RGB", self.video_size, self.bg_color)

        draw = ImageDraw.Draw(img)

        # 載入中文字型
        _, zh_font = self.load_fonts()

        # 處理中文字幕
        if zh_text and zh_text.strip():
            # 文字換行處理
            max_text_width = self.video_size[0] - 80  # 留邊距

            zh_lines = []
            for line in zh_text.split("\n"):
                if line.strip():
                    wrapped_lines = self.wrap_text(line, zh_font, max_text_width, True)
                    zh_lines.extend(wrapped_lines)

            # 計算文字位置（顯示在底部向上一點）
            line_height = self.fontsize + 10
            total_text_height = len(zh_lines) * line_height

            # 從底部向上計算起始位置
            start_y = (
                self.video_size[1] - self.subtitle_bottom_margin - total_text_height
            )

            # 繪製中文字幕
            current_y = start_y
            for line in zh_lines:
                if line.strip():
                    # 添加文字陰影效果（可選）
                    bbox = draw.textbbox((0, 0), line, font=zh_font)
                    text_width = bbox[2] - bbox[0]
                    x = (self.video_size[0] - text_width) // 2

                    # 繪製陰影
                    draw.text(
                        (x + 2, current_y + 2), line, font=zh_font, fill=(0, 0, 0)
                    )
                    # 繪製主文字
                    draw.text((x, current_y), line, font=zh_font, fill=self.text_color)
                    current_y += line_height

        return np.array(img)

    def create_dual_text_image(self, en_text, zh_text):
        """建立雙語文字圖片（英文在上，中文在下）- 保留原功能"""
        img = Image.new("RGB", self.video_size, self.bg_color)
        draw = ImageDraw.Draw(img)

        # 載入字型
        en_font, zh_font = self.load_fonts()

        # 文字換行處理
        max_text_width = self.video_size[0] - 80  # 留邊距

        # 處理英文文字換行
        en_lines = []
        if en_text and en_text.strip():
            for line in en_text.split("\n"):
                if line.strip():
                    wrapped_lines = self.wrap_text(line, en_font, max_text_width)
                    en_lines.extend(wrapped_lines)

        # 處理中文文字換行
        zh_lines = []
        if zh_text and zh_text.strip():
            for line in zh_text.split("\n"):
                if line.strip():
                    wrapped_lines = self.wrap_text(line, zh_font, max_text_width, True)
                    zh_lines.extend(wrapped_lines)

        # 計算行高和總高度
        line_height = self.fontsize + 10
        en_total_height = len(en_lines) * line_height if en_lines else 0
        zh_total_height = len(zh_lines) * line_height if zh_lines else 0
        gap_between_languages = 30 if en_lines and zh_lines else 0

        total_height = en_total_height + zh_total_height + gap_between_languages
        start_y = (self.video_size[1] - total_height) // 2

        # 繪製英文字幕
        current_y = start_y
        for line in en_lines:
            if line.strip():
                bbox = draw.textbbox((0, 0), line, font=en_font)
                text_width = bbox[2] - bbox[0]
                x = (self.video_size[0] - text_width) // 2
                draw.text((x, current_y), line, font=en_font, fill=self.text_color)
                current_y += line_height

        # 加上語言間隔
        current_y += gap_between_languages

        # 繪製中文字幕
        for line in zh_lines:
            if line.strip():
                bbox = draw.textbbox((0, 0), line, font=zh_font)
                text_width = bbox[2] - bbox[0]
                x = (self.video_size[0] - text_width) // 2
                draw.text((x, current_y), line, font=zh_font, fill=self.text_color)
                current_y += line_height

        return np.array(img)

    def merge_subtitles_single(self, zh_subtitles):
        """處理單一中文字幕列表"""
        merged = []

        for start_time, end_time, zh_text in zh_subtitles:
            if end_time:  # 確保有結束時間
                merged.append((start_time, end_time, zh_text))

        return merged

    def merge_subtitles(self, en_subtitles, zh_subtitles):
        """合併兩個字幕列表，按時間軸對齊 - 保留原功能"""
        merged = []

        # 創建時間點到字幕的對應
        all_times = set()

        # 收集所有時間點
        for start, end, _ in en_subtitles:
            all_times.add(start)
            if end:
                all_times.add(end)

        for start, end, _ in zh_subtitles:
            all_times.add(start)
            if end:
                all_times.add(end)

        all_times = sorted(all_times)

        # 為每個時間段找到對應的英文和中文字幕
        for i in range(len(all_times) - 1):
            start_time = all_times[i]
            end_time = all_times[i + 1]

            en_text = ""
            zh_text = ""

            # 找英文字幕
            for sub_start, sub_end, text in en_subtitles:
                if sub_start <= start_time and (
                    sub_end is None or sub_end > start_time
                ):
                    en_text = text
                    break

            # 找中文字幕
            for sub_start, sub_end, text in zh_subtitles:
                if sub_start <= start_time and (
                    sub_end is None or sub_end > start_time
                ):
                    zh_text = text
                    break

            if en_text or zh_text:
                merged.append((start_time, end_time, en_text, zh_text))

        return merged

    def load_audio(self, audio_file):
        """載入音檔"""
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"找不到音樂檔案 {audio_file}")

        print("載入音樂檔案...")
        self.audio = AudioFileClip(audio_file)
        print(f"音樂長度: {self.audio.duration:.2f} 秒")
        return self.audio.duration

    def load_subtitles(self, chinese_srt_file):
        """載入中文字幕檔案"""
        if not os.path.exists(chinese_srt_file):
            raise FileNotFoundError(f"找不到中文字幕檔案 {chinese_srt_file}")

        print("解析中文字幕檔案...")
        self.zh_subtitles = self.parse_subtitle_file(chinese_srt_file)

        if not self.zh_subtitles:
            raise ValueError("中文字幕檔案解析失敗或為空")

        print(f"中文字幕: {len(self.zh_subtitles)} 個片段")

    def create_video(self):
        """建立影片"""
        if not self.audio:
            raise ValueError("請先載入音檔")

        if not self.zh_subtitles:
            raise ValueError("請先載入中文字幕")

        print("處理中文字幕...")
        self.merged_subtitles = self.merge_subtitles_single(self.zh_subtitles)
        print(f"處理後共 {len(self.merged_subtitles)} 個時間段")

        print("建立影片片段...")

        if not self.merged_subtitles:
            # 如果沒有時間軸字幕，使用第一個可用的字幕顯示整個影片
            zh_text = self.zh_subtitles[0][2] if self.zh_subtitles else ""
            text_image = self.create_text_image_with_background(zh_text)
            self.video = ImageClip(text_image, duration=self.audio.duration)
        else:
            # 建立多個字幕片段
            clips = []

            for start_time, end_time, zh_text in self.merged_subtitles:
                if end_time <= self.audio.duration:
                    text_image = self.create_text_image_with_background(zh_text)
                    clip = ImageClip(text_image).set_start(start_time).set_end(end_time)
                    clips.append(clip)

            # 合成所有片段
            if clips:
                self.video = CompositeVideoClip(clips, size=self.video_size)
                self.video = self.video.set_duration(self.audio.duration)
            else:
                # 如果沒有有效字幕，顯示第一個可用字幕
                zh_text = self.zh_subtitles[0][2] if self.zh_subtitles else ""
                text_image = self.create_text_image_with_background(zh_text)
                self.video = ImageClip(text_image, duration=self.audio.duration)

        self.video = self.video.set_audio(self.audio)
        return self.video

    def export_video(self, output_file, fps=24, codec="libx264", audio_codec="aac"):
        """輸出影片"""
        if not self.video:
            raise ValueError("請先建立影片")

        print("開始輸出影片...")
        self.video.write_videofile(
            output_file, fps=fps, codec=codec, audio_codec=audio_codec
        )
        print(f"雙語字幕影片已成功輸出至: {output_file}")

    def generate_video(
        self, audio_file, chinese_srt_file, output_file, picture_file=None
    ):
        """一鍵生成影片的便捷方法"""
        try:
            # 載入背景圖片（如果有提供）
            if picture_file:
                self.load_background_image(picture_file)

            # 載入音檔和字幕
            self.load_audio(audio_file)
            self.load_subtitles(chinese_srt_file)

            # 建立並輸出影片
            self.create_video()
            self.export_video(output_file)

        except Exception as e:
            print(f"發生錯誤: {e}")
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """清理資源"""
        try:
            if self.audio:
                self.audio.close()
            if self.video:
                self.video.close()
        except:
            pass

    def __del__(self):
        """析構函數，確保資源被釋放"""
        self.cleanup()

    def get_file_paths(self, base_path, index: int) -> Dict[str, str]:

        file_name = str(index)
        return {
            "audio_file": rf"{base_path}\{file_name}.mp3",
            "english_srt_file": rf"{base_path}\{file_name}.srt",
            "chinese_srt_file": rf"{base_path}\{file_name}.zhtw.srt",
            "output_file": rf"{base_path}\{file_name}.mp4",
            "picture_file": rf"{base_path}\{file_name}.jpg",
        }

    def bat_create_mp4(self):
        paths = self.get_file_paths(r"C:\temp\0718", 2)
        audio_file = paths["audio_file"]
        english_srt_file = paths["english_srt_file"]
        chinese_srt_file = paths["chinese_srt_file"]
        output_file = paths["output_file"]
        picture_file = paths["picture_file"]
        print(paths)
        # 生成有背景圖片的影片
        self.generate_video(audio_file, chinese_srt_file, output_file, picture_file)

    def merge_mp4_videos(self, input_dir: str, output_file: str):
        """
        合併資料夾中的所有 MP4 檔案成一個影片

        Args:
            input_dir (str): MP4 檔案所在的資料夾
            output_file (str): 合併後輸出的影片路徑
        """
        input_path = Path(input_dir)
        mp4_files = sorted(input_path.glob("*.mp4"))  # 可依檔名順序排序

        if not mp4_files:
            print("❌ 找不到任何 MP4 檔案")
            return

        clips = []
        for file in mp4_files:
            print(f"📥 載入影片: {file.name}")
            clip = VideoFileClip(str(file))
            clips.append(clip)

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

        print(f"✅ 合併完成: {output_file}")


# 使用範例
if __name__ == "__main__":
    # 設定檔案路徑

    # 建立生成器實例
    generator = DualSubtitleVideoGenerator(
        video_size=(1280, 720),
        fontsize=28,
        text_color=(255, 255, 255),
        bg_color=(0, 0, 0),
        subtitle_bottom_margin=80,  # 字幕距離底部80像素
    )
    # generator.bat_create_mp4()
    generator.merge_mp4_videos(r"c:\temp\0718", r"c:\temp\0718\result.mp4")
    # 或者分步驟操作
    # generator.load_background_image(picture_file)
    # generator.load_audio(audio_file)
    # generator.load_subtitles(chinese_srt_file)
    # generator.create_video()
    # generator.export_video(output_file)
