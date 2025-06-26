import argparse
import sys
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import re
import textwrap


def parse_srt_time(time_str):
    """解析 SRT 時間格式 (HH:MM:SS,mmm)"""
    try:
        time_part, ms_part = time_str.split(",")
        h, m, s = map(int, time_part.split(":"))
        ms = int(ms_part)
        return h * 3600 + m * 60 + s + ms / 1000.0
    except:
        return 0


def parse_subtitle_file(file_path):
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
            return parse_srt_content(content)
        else:
            # 普通文字檔案
            return [(0, None, content.strip())]

    except Exception as e:
        print(f"讀取檔案錯誤 {file_path}: {e}")
        return []


def parse_srt_content(content):
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
                start_time = parse_srt_time(time_match.group(1))
                end_time = parse_srt_time(time_match.group(2))
                text = "\n".join(lines[2:])
                subtitles.append((start_time, end_time, text))

    return subtitles


def wrap_text(text, font, max_width):
    """根據字型和最大寬度自動換行"""
    words = text.split()
    lines = []
    current_line = []

    # 創建臨時 draw 物件來測量文字寬度
    temp_img = Image.new("RGB", (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    for word in words:
        # 測試加入這個詞後的行寬
        test_line = " ".join(current_line + [word])
        bbox = temp_draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                # 單個詞太長，強制換行
                lines.append(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def create_dual_text_image(
    en_text,
    zh_text,
    size=(1280, 720),
    fontsize=40,
    color=(255, 255, 255),
    bg_color=(0, 0, 0),
    en_font_path=None,
    zh_font_path=None
):
    """建立雙語文字圖片（英文在上，中文在下）"""
    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)

    # 載入字型
    try:
        # 預設英文字型路徑
        default_en_font_paths = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ]

        # 預設中文字型路徑
        default_zh_font_paths = [
            r"C:\Windows\Fonts\msjh.ttc",
            r"C:\Windows\Fonts\simsun.ttc",
            r"C:\Windows\Fonts\mingliu.ttc",
        ]

        en_font = None
        zh_font = None

        # 載入英文字型
        if en_font_path and os.path.exists(en_font_path):
            en_font = ImageFont.truetype(en_font_path, fontsize)
        else:
            for font_path in default_en_font_paths:
                if os.path.exists(font_path):
                    en_font = ImageFont.truetype(font_path, fontsize)
                    break

        # 載入中文字型
        if zh_font_path and os.path.exists(zh_font_path):
            zh_font = ImageFont.truetype(zh_font_path, fontsize)
        else:
            for font_path in default_zh_font_paths:
                if os.path.exists(font_path):
                    zh_font = ImageFont.truetype(font_path, fontsize)
                    break

        if en_font is None:
            en_font = ImageFont.load_default()
        if zh_font is None:
            zh_font = ImageFont.load_default()

    except:
        en_font = ImageFont.load_default()
        zh_font = ImageFont.load_default()

    # 文字換行處理
    max_text_width = size[0] - 80  # 留邊距

    # 處理英文文字換行
    en_lines = []
    if en_text and en_text.strip():
        for line in en_text.split("\n"):
            if line.strip():
                wrapped_lines = wrap_text(line, en_font, max_text_width)
                en_lines.extend(wrapped_lines)

    # 處理中文文字換行
    zh_lines = []
    if zh_text and zh_text.strip():
        for line in zh_text.split("\n"):
            if line.strip():
                wrapped_lines = wrap_text(line, zh_font, max_text_width)
                zh_lines.extend(wrapped_lines)

    # 計算行高和總高度
    line_height = fontsize + 10
    en_total_height = len(en_lines) * line_height if en_lines else 0
    zh_total_height = len(zh_lines) * line_height if zh_lines else 0
    gap_between_languages = 30 if en_lines and zh_lines else 0

    total_height = en_total_height + zh_total_height + gap_between_languages
    start_y = (size[1] - total_height) // 2

    # 繪製英文字幕
    current_y = start_y
    for line in en_lines:
        if line.strip():
            bbox = draw.textbbox((0, 0), line, font=en_font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            draw.text((x, current_y), line, font=en_font, fill=color)
            current_y += line_height

    # 加上語言間隔
    current_y += gap_between_languages

    # 繪製中文字幕
    for line in zh_lines:
        if line.strip():
            bbox = draw.textbbox((0, 0), line, font=zh_font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            draw.text((x, current_y), line, font=zh_font, fill=color)
            current_y += line_height

    return np.array(img)


def merge_subtitles(en_subtitles, zh_subtitles):
    """合併兩個字幕列表，按時間軸對齊"""
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
            if sub_start <= start_time and (sub_end is None or sub_end > start_time):
                en_text = text
                break

        # 找中文字幕
        for sub_start, sub_end, text in zh_subtitles:
            if sub_start <= start_time and (sub_end is None or sub_end > start_time):
                zh_text = text
                break

        if en_text or zh_text:
            merged.append((start_time, end_time, en_text, zh_text))

    return merged


def create_dual_subtitle_video(args):
    """主要函數：建立雙語字幕影片"""
    try:
        # 檢查檔案
        if not os.path.exists(args.audio):
            print(f"錯誤：找不到音樂檔案 {args.audio}")
            return False

        if not os.path.exists(args.english_srt):
            print(f"錯誤：找不到英文字幕檔案 {args.english_srt}")
            return False

        if not os.path.exists(args.chinese_srt):
            print(f"錯誤：找不到中文字幕檔案 {args.chinese_srt}")
            return False

        # 解析字幕檔案
        print("解析字幕檔案...")
        en_subtitles = parse_subtitle_file(args.english_srt)
        zh_subtitles = parse_subtitle_file(args.chinese_srt)

        if not en_subtitles and not zh_subtitles:
            print("所有字幕檔案解析失敗或為空")
            return False

        print(f"英文字幕: {len(en_subtitles)} 個片段")
        print(f"中文字幕: {len(zh_subtitles)} 個片段")

        # 載入音樂
        print("載入音樂檔案...")
        audio = AudioFileClip(args.audio)
        duration = audio.duration
        print(f"音樂長度: {duration:.2f} 秒")

        # 合併字幕
        print("合併雙語字幕...")
        merged_subtitles = merge_subtitles(en_subtitles, zh_subtitles)
        print(f"合併後共 {len(merged_subtitles)} 個時間段")

        # 建立影片片段
        print("建立影片片段...")
        
        # 解析視頻尺寸
        video_size = tuple(map(int, args.size.split('x')))
        
        # 解析字體顏色
        text_color = tuple(map(int, args.text_color.split(',')))
        
        # 解析背景顏色
        bg_color = tuple(map(int, args.bg_color.split(',')))

        if not merged_subtitles:
            # 如果沒有時間軸字幕，使用第一個可用的字幕顯示整個影片
            en_text = en_subtitles[0][2] if en_subtitles else ""
            zh_text = zh_subtitles[0][2] if zh_subtitles else ""
            text_image = create_dual_text_image(
                en_text, zh_text, 
                size=video_size,
                fontsize=args.fontsize,
                color=text_color,
                bg_color=bg_color,
                en_font_path=args.en_font,
                zh_font_path=args.zh_font
            )
            video = ImageClip(text_image, duration=duration)
        else:
            # 建立多個字幕片段
            clips = []

            for start_time, end_time, en_text, zh_text in merged_subtitles:
                if end_time <= duration:
                    text_image = create_dual_text_image(
                        en_text, zh_text,
                        size=video_size,
                        fontsize=args.fontsize,
                        color=text_color,
                        bg_color=bg_color,
                        en_font_path=args.en_font,
                        zh_font_path=args.zh_font
                    )
                    clip = ImageClip(text_image).set_start(start_time).set_end(end_time)
                    clips.append(clip)

            # 合成所有片段
            if clips:
                video = CompositeVideoClip(clips, size=video_size)
                video = video.set_duration(duration)
            else:
                # 如果沒有有效字幕，顯示第一個可用字幕
                en_text = en_subtitles[0][2] if en_subtitles else ""
                zh_text = zh_subtitles[0][2] if zh_subtitles else ""
                text_image = create_dual_text_image(
                    en_text, zh_text,
                    size=video_size,
                    fontsize=args.fontsize,
                    color=text_color,
                    bg_color=bg_color,
                    en_font_path=args.en_font,
                    zh_font_path=args.zh_font
                )
                video = ImageClip(text_image, duration=duration)

        video = video.set_audio(audio)

        # 輸出影片
        print("開始輸出影片...")
        video.write_videofile(
            args.output, 
            fps=args.fps, 
            codec=args.codec, 
            audio_codec=args.audio_codec
        )

        print(f"雙語字幕影片已成功輸出至: {args.output}")
        return True

    except Exception as e:
        print(f"發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 釋放資源
        try:
            if "audio" in locals():
                audio.close()
            if "video" in locals():
                video.close()
        except:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="雙語字幕影片生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python dual_subtitle_generator.py -a audio.mp3 -e english.srt -c chinese.srt -o output.mp4
  python dual_subtitle_generator.py -a audio.mp3 -e english.srt -c chinese.srt -o output.mp4 --fontsize 50 --size 1920x1080
  python dual_subtitle_generator.py -a audio.mp3 -e english.srt -c chinese.srt -o output.mp4 --text-color "255,255,0" --bg-color "0,0,255"
        """
    )

    # 必要參數
    parser.add_argument(
        "-a", "--audio", 
        required=True, 
        help="音頻檔案路徑 (支援 mp3, wav, m4a 等格式)"
    )
    parser.add_argument(
        "-e", "--english-srt", 
        required=True, 
        help="英文字幕檔案路徑 (.srt 格式)"
    )
    parser.add_argument(
        "-c", "--chinese-srt", 
        required=True, 
        help="中文字幕檔案路徑 (.srt 格式)"
    )
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="輸出影片檔案路徑 (.mp4 格式)"
    )

    # 可選參數
    parser.add_argument(
        "--size", 
        default="1280x720", 
        help="影片尺寸 (格式: 寬x高, 預設: 1280x720)"
    )
    parser.add_argument(
        "--fontsize", 
        type=int, 
        default=40, 
        help="字體大小 (預設: 40)"
    )
    parser.add_argument(
        "--text-color", 
        default="255,255,255", 
        help="文字顏色 RGB (格式: R,G,B, 預設: 255,255,255 白色)"
    )
    parser.add_argument(
        "--bg-color", 
        default="0,0,0", 
        help="背景顏色 RGB (格式: R,G,B, 預設: 0,0,0 黑色)"
    )
    parser.add_argument(
        "--en-font", 
        help="英文字體檔案路徑 (可選，不指定將使用系統預設字體)"
    )
    parser.add_argument(
        "--zh-font", 
        help="中文字體檔案路徑 (可選，不指定將使用系統預設字體)"
    )
    parser.add_argument(
        "--fps", 
        type=int, 
        default=24, 
        help="影片幀率 (預設: 24)"
    )
    parser.add_argument(
        "--codec", 
        default="libx264", 
        help="影片編碼器 (預設: libx264)"
    )
    parser.add_argument(
        "--audio-codec", 
        default="aac", 
        help="音頻編碼器 (預設: aac)"
    )

    args = parser.parse_args()

    # 驗證參數
    try:
        # 驗證尺寸格式
        if 'x' not in args.size or len(args.size.split('x')) != 2:
            print("錯誤：影片尺寸格式不正確，應為 '寬x高' 格式，例如：1280x720")
            sys.exit(1)
        
        width, height = map(int, args.size.split('x'))
        if width <= 0 or height <= 0:
            print("錯誤：影片尺寸必須為正數")
            sys.exit(1)

        # 驗證顏色格式
        def validate_color(color_str, color_name):
            try:
                rgb = list(map(int, color_str.split(',')))
                if len(rgb) != 3 or any(c < 0 or c > 255 for c in rgb):
                    raise ValueError
                return rgb
            except ValueError:
                print(f"錯誤：{color_name}格式不正確，應為 'R,G,B' 格式，例如：255,255,255")
                sys.exit(1)

        validate_color(args.text_color, "文字顏色")
        validate_color(args.bg_color, "背景顏色")

        # 驗證字體大小
        if args.fontsize <= 0:
            print("錯誤：字體大小必須為正數")
            sys.exit(1)

        # 驗證幀率
        if args.fps <= 0:
            print("錯誤：幀率必須為正數")
            sys.exit(1)

    except ValueError as e:
        print(f"參數驗證錯誤：{e}")
        sys.exit(1)

    # 顯示配置信息
    print("=" * 50)
    print("雙語字幕影片生成器")
    print("=" * 50)
    print(f"音頻檔案: {args.audio}")
    print(f"英文字幕: {args.english_srt}")
    print(f"中文字幕: {args.chinese_srt}")
    print(f"輸出檔案: {args.output}")
    print(f"影片尺寸: {args.size}")
    print(f"字體大小: {args.fontsize}")
    print(f"文字顏色: {args.text_color}")
    print(f"背景顏色: {args.bg_color}")
    print(f"幀率: {args.fps}")
    print("=" * 50)

    # 執行主要功能
    success = create_dual_subtitle_video(args)
    
    if success:
        print("\n✅ 影片生成完成！")
        sys.exit(0)
    else:
        print("\n❌ 影片生成失敗！")
        sys.exit(1)


if __name__ == "__main__":
    main()