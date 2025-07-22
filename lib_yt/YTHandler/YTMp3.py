from datetime import timedelta
import os
import re
from googletrans import Translator
import requests
from yt_dlp import YoutubeDL


async def download_mp3_from_info(info: dict, output_dir: str) -> str:
    """根據已取得的 info 字典下載 MP3 音訊"""
    video_id = info.get("id", "audio")
    output_filename = f"{video_id}.mp3"
    output_path = os.path.join(output_dir, output_filename)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": os.path.join(output_dir, f"temp_{video_id}.%(ext)s"),
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # 用原始 URL 再下載音訊
            ydl.download([info["webpage_url"]])

        # 找出實際的下載檔案
        temp_path = os.path.join(output_dir, f"temp_{video_id}.mp3")
        if os.path.exists(temp_path):
            os.rename(temp_path, output_path)
            print(f"✅ 音訊已下載並儲存為：{output_path}")
            return output_path

        print("❌ 找不到 mp3 檔案")
        return ""
    except Exception as e:
        print(f"❌ 下載 MP3 錯誤: {e}")
        raise


async def download_thumbnail_from_info(
    info: dict, output_dir: str, use_video_id: bool = True
) -> str:
    """從已取得的 info 字典下載縮圖圖片"""

    thumbnail_url = info.get("thumbnail", "")
    video_id = info.get("id", "thumbnail")

    if not thumbnail_url:
        print("❌ 無法取得縮圖網址")
        return ""

    # 判斷副檔名
    ext = "jpg"
    for t in [".jpeg", ".png", ".webp"]:
        if t in thumbnail_url.lower():
            ext = t.strip(".")
            break
    if ext == "webp":
        ext = "jpg"

    filename = f"{video_id}.{ext}" if use_video_id else f"thumbnail.{ext}"
    output_path = os.path.join(output_dir, filename)

    try:
        print(f"🖼 下載縮圖中：{thumbnail_url}")
        response = requests.get(thumbnail_url, stream=True, timeout=30)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        print(f"✅ 縮圖已儲存至：{output_path}")
        return output_path

    except requests.RequestException as e:
        print(f"❌ 網路錯誤: {e}")
        return ""
    except Exception as e:
        print(f"❌ 下載縮圖發生錯誤: {e}")
        return ""


def parse_timestamp(timestamp: str) -> float:
    """將 SRT 時間格式轉為秒數"""
    h, m, s_ms = timestamp.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def format_timestamp(seconds: float) -> str:
    """將秒數轉回 SRT 時間格式"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    ms = int((td.total_seconds() - total_seconds) * 1000)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# 英文使用 ? 可以先不用
def merge_srt_to_sentence_srt(input_srt_path: str, output_srt_path: str):
    with open(input_srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())

    merged_segments = []
    buffer_text = ""
    buffer_start = None
    buffer_end = None

    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue

        time_range = lines[1]
        text = " ".join(lines[2:]).strip()

        start_str, end_str = time_range.split(" --> ")
        start_sec = parse_timestamp(start_str)
        end_sec = parse_timestamp(end_str)

        if buffer_text == "":
            buffer_start = start_sec

        buffer_text += (" " if buffer_text else "") + text
        buffer_end = end_sec

        if re.search(r'[.!?]["”]?$|\w\.\s*$', text):
            merged_segments.append((buffer_start, buffer_end, buffer_text.strip()))
            buffer_text = ""
            buffer_start = None
            buffer_end = None

    # 殘留最後一句
    if buffer_text:
        merged_segments.append((buffer_start, buffer_end, buffer_text.strip()))

    # 寫入新的 SRT 檔案
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for idx, (start, end, text) in enumerate(merged_segments, start=1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")

    print(f"[輸出完成] 新的合併字幕已寫入：{output_srt_path}")


def translate_text(text, target_lang):
    translator = Translator()
    if not text.strip():
        return ""
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print(f"⚠️ 翻譯失敗: {e}")
        return ""


# 翻譯字幕
async def process_srt(input_path, output_path, target_lang):
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    output_lines = []
    buffer = []
    blocks = []
    for line in lines:
        if re.match(r"^\d+$", line.strip()):
            if buffer:
                blocks.append(list(buffer))
                buffer.clear()
        buffer.append(line)
    if buffer:
        blocks.append(list(buffer))

    total = len(blocks)
    for i, block in enumerate(blocks, start=1):
        output_lines.extend(process_block(block, target_lang))
        print(f"⏳ 處理進度: {i}/{total} ({(i/total)*100:.1f}%)", end="\r")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(output_lines)


def process_block(block_lines, target_lang):
    result = []
    text_lines = []
    block_number = ""
    timecode_line = ""

    for line in block_lines:
        if line.strip().isdigit():
            block_number = line
        elif "-->" in line:
            timecode_line = line
        else:
            text_lines.append(line.strip())

    if text_lines:
        full_text = " ".join(text_lines)
        translated = translate_text(full_text, target_lang)
        # 合併為單行字幕
        merged_line = f"{full_text}\n{translated}\n"
        result.extend([block_number, timecode_line, merged_line, "\n"])
    else:
        result.extend(block_lines)
        result.append("\n")

    return result


import torch
from faster_whisper import WhisperModel


def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# medium
async def transcribe_mp3_to_srt(
    mp3_path: str, output_srt_path: str, model_size="small"
) -> dict:
    """使用 FasterWhisper 將 MP3 轉為 SRT 字幕"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[FasterWhisper] 初始化模型 {model_size} on {device}")

    model = WhisperModel(model_size, device=device, compute_type="int8")
    print(f"[FasterWhisper] 開始轉錄：{mp3_path}")
    segments, info = model.transcribe(mp3_path, beam_size=5)
    print(f"[FasterWhisper] 偵測語言：{info.language}")

    with open(output_srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(
                f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n"
            )
            f.write(f"{segment.text.strip()}\n\n")

    print(f"✅ SRT 已儲存：{output_srt_path}")
    return {"srt_path": output_srt_path, "lan": info.language}
