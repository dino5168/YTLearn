from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import re

# === 1. 設定檔案路徑 ===
audio_file = r"c:\mp3\01.mp3"
str_file = r"c:\mp3\01.srt"  # 或 .srt 檔案
output_file = r"c:\mp3\output.mp4"

def parse_srt_time(time_str):
    """解析 SRT 時間格式 (HH:MM:SS,mmm)"""
    try:
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        return h * 3600 + m * 60 + s + ms / 1000.0
    except:
        return 0

def parse_subtitle_file(file_path):
    """解析字幕檔案"""
    try:
        # 嘗試不同編碼
        encodings = ['utf-8', 'utf-8-sig', 'big5', 'gbk', 'cp950']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"成功使用 {encoding} 編碼")
                break
            except:
                continue
        
        if not content:
            raise Exception("無法讀取檔案")
        
        # 檢查是否為 SRT 格式
        if re.search(r'\d+:\d+:\d+,\d+\s*-->\s*\d+:\d+:\d+,\d+', content):
            return parse_srt_content(content)
        else:
            # 普通文字檔案
            return [(0, None, content.strip())]
            
    except Exception as e:
        print(f"讀取檔案錯誤: {e}")
        return []

def parse_srt_content(content):
    """解析 SRT 內容"""
    subtitles = []
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # 第一行是序號
            # 第二行是時間
            time_line = lines[1]
            time_match = re.search(r'(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)', time_line)
            
            if time_match:
                start_time = parse_srt_time(time_match.group(1))
                end_time = parse_srt_time(time_match.group(2))
                text = '\n'.join(lines[2:])
                subtitles.append((start_time, end_time, text))
    
    return subtitles

def create_text_image(text, size=(1280, 720), fontsize=50, color=(255, 255, 255), bg_color=(0, 0, 0)):
    """建立文字圖片"""
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # 載入字型
    try:
        font_paths = [
            r"C:\Windows\Fonts\msjh.ttc",
            r"C:\Windows\Fonts\simsun.ttc",
            r"C:\Windows\Fonts\mingliu.ttc",
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, fontsize)
                break
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # 處理多行文字
    lines = text.split('\n')
    line_height = fontsize + 10
    total_height = len(lines) * line_height
    start_y = (size[1] - total_height) // 2
    
    for i, line in enumerate(lines):
        if line.strip():
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            y = start_y + i * line_height
            draw.text((x, y), line, font=font, fill=color)
    
    return np.array(img)

try:
    # 檢查檔案
    if not os.path.exists(audio_file):
        print(f"錯誤：找不到音樂檔案 {audio_file}")
        exit()
    
    if not os.path.exists(str_file):
        print(f"錯誤：找不到字幕檔案 {str_file}")
        exit()
    
    # === 2. 解析字幕檔案 ===
    print("解析字幕檔案...")
    subtitles = parse_subtitle_file(str_file)
    
    if not subtitles:
        print("字幕檔案解析失敗或為空")
        exit()
    
    print(f"找到 {len(subtitles)} 個字幕片段")
    
    # === 3. 載入音樂 ===
    print("載入音樂檔案...")
    audio = AudioFileClip(audio_file)
    duration = audio.duration
    print(f"音樂長度: {duration:.2f} 秒")
    
    # === 4. 建立影片片段 ===
    print("建立影片片段...")
    
    if len(subtitles) == 1 and subtitles[0][1] is None:
        # 單一文字，顯示整個音樂長度
        text_image = create_text_image(subtitles[0][2])
        video = ImageClip(text_image, duration=duration)
    else:
        # 多個字幕片段
        clips = []
        
        # 建立黑色背景
        black_image = create_text_image("")
        
        for start_time, end_time, text in subtitles:
            if end_time and end_time <= duration:
                text_image = create_text_image(text)
                clip = ImageClip(text_image).set_start(start_time).set_end(end_time)
                clips.append(clip)
        
        # 合成所有片段
        if clips:
            video = CompositeVideoClip(clips, size=(1280, 720))
            video = video.set_duration(duration)
        else:
            # 如果沒有有效字幕，顯示第一個字幕
            text_image = create_text_image(subtitles[0][2])
            video = ImageClip(text_image, duration=duration)
    
    video = video.set_audio(audio)
    
    # === 5. 輸出影片 ===
    print("開始輸出影片...")
    video.write_videofile(
        output_file, 
        fps=24,
        codec='libx264',
        audio_codec='aac'
    )
    
    print(f"影片已成功輸出至: {output_file}")
    
except Exception as e:
    print(f"發生錯誤: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # 釋放資源
    try:
        if 'audio' in locals():
            audio.close()
        if 'video' in locals():
            video.close()
    except:
        pass