import yt_dlp
import os
import re
from datetime import datetime, timedelta
from googletrans import Translator

# 初始化翻譯器
translator = Translator()

# 固定路徑
OUTPUT_FOLDER = "c:\\temp"
ORIGINAL_SRT = os.path.join(OUTPUT_FOLDER, "a.srt")  # 純英文
BILINGUAL_SRT = os.path.join(OUTPUT_FOLDER, "b.srt")  # 英中雙語
CHINESE_SRT = os.path.join(OUTPUT_FOLDER, "c.srt")  # 純中文
ADJUSTED_SRT = os.path.join(OUTPUT_FOLDER, "d.srt")  # 調整後英中雙語

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
    """翻譯 SRT 檔案，產生英中雙語和純中文兩個版本"""
    if not os.path.exists(ORIGINAL_SRT):
        print(f"❌ 找不到原始字幕檔案: {ORIGINAL_SRT}")
        return False

    print("🔠 開始將英文字幕翻譯成中文...")

    with open(ORIGINAL_SRT, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    bilingual_lines = []  # 英中雙語
    chinese_lines = []  # 純中文
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
        bilingual_block, chinese_block = process_block_dual(block)
        bilingual_lines.extend(bilingual_block)
        chinese_lines.extend(chinese_block)
        print(f"⏳ 翻譯進度: {i}/{total} ({(i/total)*100:.1f}%)", end="\r")

    # 寫入英中雙語字幕檔案
    with open(BILINGUAL_SRT, "w", encoding="utf-8") as outfile:
        outfile.writelines(bilingual_lines)

    # 寫入純中文字幕檔案
    with open(CHINESE_SRT, "w", encoding="utf-8") as outfile:
        outfile.writelines(chinese_lines)

    print(f"\n✅ 英中雙語字幕翻譯完成並儲存為: {BILINGUAL_SRT}")
    print(f"✅ 純中文字幕翻譯完成並儲存為: {CHINESE_SRT}")
    return True


def process_block_dual(block_lines):
    """處理單個字幕塊，回傳英中雙語和純中文兩個版本"""
    bilingual_result = []
    chinese_result = []
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

        # 英中雙語字幕（英文在上，中文在下）
        bilingual_content = f"{full_text}\n{translated}\n"
        bilingual_result.extend([block_number, timecode_line, bilingual_content, "\n"])

        # 純中文字幕
        chinese_content = f"{translated}\n"
        chinese_result.extend([block_number, timecode_line, chinese_content, "\n"])
    else:
        bilingual_result.extend(block_lines)
        bilingual_result.append("\n")
        chinese_result.extend(block_lines)
        chinese_result.append("\n")

    return bilingual_result, chinese_result


def parse_time_adj(t):
    """解析時間（用於調整功能）"""
    return datetime.strptime(t, TIME_FORMAT)


def format_time_adj(t):
    """格式化時間（用於調整功能）"""
    return t.strftime(TIME_FORMAT)[:-3]  # 去掉最後3位微秒，只留到毫秒


def adjust_subtitle_timing():
    """調整字幕時間軸（基於英中雙語字幕）"""
    if not os.path.exists(BILINGUAL_SRT):
        print(f"❌ 找不到英中雙語字幕檔案: {BILINGUAL_SRT}")
        return False

    print("🔧 開始調整英中雙語字幕時間軸...")

    with open(BILINGUAL_SRT, "r", encoding="utf-8") as f:
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
    print("功能：下載英文字幕 → 翻譯成英中雙語+純中文 → 調整時間軸")
    print("輸出檔案：")
    print(f"  a.srt (英文字幕): {ORIGINAL_SRT}")
    print(f"  b.srt (英中雙語): {BILINGUAL_SRT}")
    print(f"  c.srt (純中文): {CHINESE_SRT}")
    print(f"  d.srt (調整後英中雙語): {ADJUSTED_SRT}")
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

    # 步驟2：翻譯成英中雙語和純中文字幕
    print("\n🌐 步驟2：翻譯成英中雙語和純中文字幕...")
    if not translate_srt():
        return

    # 步驟3：調整英中雙語字幕時間軸
    print("\n⏰ 步驟3：調整英中雙語字幕時間軸...")
    if not adjust_subtitle_timing():
        return

    print("\n🎉 所有步驟完成！")
    print("檔案清單：")
    print(f"  📄 a.srt (英文字幕): {ORIGINAL_SRT}")
    print(f"  📄 b.srt (英中雙語): {BILINGUAL_SRT}")
    print(f"  📄 c.srt (純中文): {CHINESE_SRT}")
    print(f"  📄 d.srt (調整後英中雙語): {ADJUSTED_SRT}")


if __name__ == "__main__":
    main()
