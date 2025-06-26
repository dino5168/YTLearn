import yt_dlp
import os
import re
from datetime import datetime, timedelta
from googletrans import Translator

# 初始化翻譯器
translator = Translator()

# 固定路徑
OUTPUT_FOLDER = "c:\\temp"
ORIGINAL_SRT = os.path.join(OUTPUT_FOLDER, "a.srt")
TRANSLATED_SRT = os.path.join(OUTPUT_FOLDER, "b.srt")
ADJUSTED_SRT = os.path.join(OUTPUT_FOLDER, "c.srt")

TIME_FORMAT = "%H:%M:%S,%f"


def parse_srt_time(time_str):
    """解析 SRT 時間格式"""
    time_str = time_str.replace(",", ".")
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    return timedelta(
        hours=time_obj.hour,
        minutes=time_obj.minute,
        seconds=time_obj.second,
        microseconds=time_obj.microsecond,
    )


def format_srt_time(time_delta):
    """格式化時間為 SRT 格式"""
    total_seconds = int(time_delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = time_delta.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def clean_subtitle_content(content):
    """清理字幕內容，移除重複和無用標籤"""
    # 移除 HTML 標籤
    content = re.sub(r"<[^>]+>", "", content)
    # 移除多餘空白
    content = re.sub(r"\s+", " ", content).strip()
    # 移除重複的標點符號
    content = re.sub(r"[.]{2,}", "...", content)
    content = re.sub(r"[?]{2,}", "?", content)
    content = re.sub(r"[!]{2,}", "!", content)
    return content


def remove_duplicate_subtitles(srt_content):
    """移除重複的字幕條目"""
    subtitle_blocks = re.split(r"\n\s*\n", srt_content.strip())
    cleaned_subtitles = []
    previous_content = ""
    previous_end_time = None

    for block in subtitle_blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        try:
            subtitle_id = lines[0]
            time_line = lines[1]
            content_lines = lines[2:]

            time_match = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line
            )
            if not time_match:
                continue

            start_time_str, end_time_str = time_match.groups()
            start_time = parse_srt_time(start_time_str)
            end_time = parse_srt_time(end_time_str)

            content = " ".join(content_lines)
            content = clean_subtitle_content(content)

            if content == previous_content:
                continue

            if previous_end_time and start_time < previous_end_time:
                start_time = previous_end_time + timedelta(milliseconds=1)
                if start_time >= end_time:
                    continue

            duration = end_time - start_time
            if duration.total_seconds() < 0.1:
                continue

            start_time_str = format_srt_time(start_time)
            end_time_str = format_srt_time(end_time)

            cleaned_block = f"{len(cleaned_subtitles) + 1}\n{start_time_str} --> {end_time_str}\n{content}"
            cleaned_subtitles.append(cleaned_block)

            previous_content = content
            previous_end_time = end_time

        except Exception as e:
            print(f"處理字幕塊時出錯: {e}")
            continue

    return "\n\n".join(cleaned_subtitles)


def download_youtube_subtitles(url: str):
    """下載 YouTube 字幕為 SRT 格式"""
    # 確保輸出資料夾存在
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "outtmpl": f"{OUTPUT_FOLDER}/%(title)s.%(ext)s",
        "subtitlesformat": "srt",
        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 找到下載的字幕檔案並重命名為 a.srt
        srt_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".srt")]
        if srt_files:
            downloaded_file = os.path.join(OUTPUT_FOLDER, srt_files[0])

            # 讀取並清理字幕
            with open(downloaded_file, "r", encoding="utf-8") as f:
                original_content = f.read()

            cleaned_content = remove_duplicate_subtitles(original_content)

            # 寫入到固定檔名
            with open(ORIGINAL_SRT, "w", encoding="utf-8") as f:
                f.write(cleaned_content)

            # 刪除原始下載檔案（如果不是 a.srt）
            if downloaded_file != ORIGINAL_SRT:
                os.remove(downloaded_file)

            print(f"✅ 英文字幕下載完成並儲存為: {ORIGINAL_SRT}")
            return True
        else:
            print("❌ 沒有找到下載的字幕檔案")
            return False

    except Exception as e:
        print(f"❌ 下載失敗：{e}")
        return False


def translate_text(text, target_lang="zh-TW"):
    """翻譯文字"""
    if not text.strip():
        return ""
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print(f"⚠️ 翻譯失敗: {e}")
        return text  # 翻譯失敗時返回原文


def translate_srt():
    """翻譯 SRT 檔案"""
    if not os.path.exists(ORIGINAL_SRT):
        print(f"❌ 找不到原始字幕檔案: {ORIGINAL_SRT}")
        return False

    print("🔠 開始將英文字幕翻譯成中文...")

    with open(ORIGINAL_SRT, "r", encoding="utf-8") as infile:
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
        output_lines.extend(process_block(block))
        print(f"⏳ 翻譯進度: {i}/{total} ({(i/total)*100:.1f}%)", end="\r")

    with open(TRANSLATED_SRT, "w", encoding="utf-8") as outfile:
        outfile.writelines(output_lines)

    print(f"\n✅ 英中雙語字幕翻譯完成並儲存為: {TRANSLATED_SRT}")
    return True


def process_block(block_lines):
    """處理單個字幕塊"""
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
        translated = translate_text(full_text)
        # 合併為英中雙語字幕（英文在上，中文在下）
        merged_line = f"{full_text}\n{translated}\n"
        result.extend([block_number, timecode_line, merged_line, "\n"])
    else:
        result.extend(block_lines)
        result.append("\n")

    return result


def parse_time_adj(t):
    """解析時間（用於調整功能）"""
    return datetime.strptime(t, TIME_FORMAT)


def format_time_adj(t):
    """格式化時間（用於調整功能）"""
    return t.strftime(TIME_FORMAT)[:-3]  # 去掉最後3位微秒，只留到毫秒


def adjust_subtitle_timing():
    """調整字幕時間軸"""
    if not os.path.exists(TRANSLATED_SRT):
        print(f"❌ 找不到翻譯後字幕檔案: {TRANSLATED_SRT}")
        return False

    print("🔧 開始調整字幕時間軸...")

    with open(TRANSLATED_SRT, "r", encoding="utf-8") as f:
        content = f.read()

    # 用正則切割每段字幕
    blocks_raw = re.split(r"\n\s*\n", content.strip())
    blocks = []

    for block in blocks_raw:
        lines = block.splitlines()
        if len(lines) < 3:
            continue  # 不完整跳過

        idx = lines[0].strip()
        times = lines[1].strip()
        en = lines[2].strip()
        zh = lines[3].strip() if len(lines) > 3 else ""

        m = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", times
        )
        if not m:
            continue  # 格式錯誤跳過

        start = parse_time_adj(m.group(1))
        end = parse_time_adj(m.group(2))

        blocks.append({"idx": idx, "start": start, "end": end, "en": en, "zh": zh})

    # 調整結束時間
    for i in range(len(blocks) - 1):
        blocks[i]["end"] = blocks[i + 1]["start"]

    # 寫入調整後的檔案
    with open(ADJUSTED_SRT, "w", encoding="utf-8") as f:
        for b in blocks:
            f.write(f"{b['idx']}\n")
            f.write(f"{format_time_adj(b['start'])} --> {format_time_adj(b['end'])}\n")
            f.write(f"{b['en']}\n")
            if b["zh"]:
                f.write(f"{b['zh']}\n")
            f.write("\n")

    print(f"✅ 時間軸調整完成並儲存為: {ADJUSTED_SRT}")
    return True


def main():
    """主程式"""
    print("🎬 整合式 YouTube 字幕處理器")
    print("=" * 50)
    print("功能：下載英文字幕 → 翻譯成英中雙語 → 調整時間軸")
    print("輸出檔案：")
    print(f"  英文字幕: {ORIGINAL_SRT}")
    print(f"  英中雙語: {TRANSLATED_SRT}")
    print(f"  調整後雙語: {ADJUSTED_SRT}")
    print("=" * 50)

    # 獲取 YouTube 網址
    youtube_url = input("請輸入 YouTube 影片網址：").strip()

    if not youtube_url:
        print("❌ 網址不能為空！")
        return

    # 步驟1：下載英文字幕
    print("\n📥 步驟1：下載英文字幕...")
    if not download_youtube_subtitles(youtube_url):
        return

    # 步驟2：翻譯成英中雙語字幕
    print("\n🌐 步驟2：翻譯成英中雙語字幕...")
    if not translate_srt():
        return

    # 步驟3：調整雙語字幕時間軸
    print("\n⏰ 步驟3：調整雙語字幕時間軸...")
    if not adjust_subtitle_timing():
        return

    print("\n🎉 所有步驟完成！")
    print(f"最終英中雙語字幕檔案：{ADJUSTED_SRT}")


if __name__ == "__main__":
    main()
