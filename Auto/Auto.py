import yt_dlp
import os
import re
import subprocess
import pysrt
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from googletrans import Translator

# 初始化翻譯器
translator = Translator()

# 固定路徑配置
BASE_DIR = "c:\\temp"
VIDEO_PATH = os.path.join(BASE_DIR, "video.mp4")
ORIGINAL_SRT = os.path.join(BASE_DIR, "a.srt")  # 純英文
BILINGUAL_SRT = os.path.join(BASE_DIR, "b.srt")  # 英中雙語
CHINESE_SRT = os.path.join(BASE_DIR, "c.srt")  # 純中文
ADJUSTED_SRT = os.path.join(BASE_DIR, "d.srt")  # 調整後英中雙語
RESULT_DIR = os.path.join(BASE_DIR, "result")  # 轉換圖片的輸出目錄
RESULTX_DIR = os.path.join(BASE_DIR, "resultx")  # 加入字幕的圖片
FINAL_PDF = os.path.join(BASE_DIR, "result.pdf")  # 最終PDF

TIME_FORMAT = "%H:%M:%S,%f"


def ensure_directories():
    """確保所有必要目錄存在"""
    directories = [BASE_DIR, RESULT_DIR, RESULTX_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 建立目錄：{directory}")


def clean_directory(directory):
    """清理目錄中的檔案"""
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)


# ===== 字幕處理相關函數 =====
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
    content = re.sub(r"<[^>]+>", "", content)
    content = re.sub(r"\s+", " ", content).strip()
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


# ===== 步驟1：下載影片和字幕 =====
def download_youtube_video_and_subtitles(url):
    """下載 YouTube 影片和字幕"""
    print("📥 步驟1：下載 YouTube 影片和字幕...")

    ensure_directories()

    # 下載影片
    print("🎬 下載影片...")
    video_success = download_video(url)
    if not video_success:
        return False

    # 下載字幕
    print("📝 下載字幕...")
    subtitle_success = download_subtitles(url)
    if not subtitle_success:
        return False

    return True


def download_video(url):
    """下載影片"""
    format_options = [
        "bestvideo[height<=720]+bestaudio",
        "bestvideo+bestaudio",
        "best",
        "worst",
    ]

    for i, format_option in enumerate(format_options):
        print(f"嘗試格式選項 {i+1}: {format_option}")

        ydl_opts = {
            "format": format_option,
            "outtmpl": VIDEO_PATH.replace(".mp4", ".%(ext)s"),
            "no_warnings": False,
            "quiet": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

                # 尋找下載的影片檔案並重命名
                for ext in ["mp4", "mkv", "webm", "avi"]:
                    temp_file = VIDEO_PATH.replace(".mp4", f".{ext}")
                    if os.path.exists(temp_file):
                        if temp_file != VIDEO_PATH:
                            os.rename(temp_file, VIDEO_PATH)
                        print(f"✅ 影片下載完成：{VIDEO_PATH}")
                        return True

        except Exception as e:
            print(f"❌ 格式選項 {i+1} 失敗: {str(e)}")
            continue

    print("❌ 所有格式選項都失敗了")
    return False


def download_subtitles(url):
    """下載字幕"""
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "outtmpl": f"{BASE_DIR}/%(title)s.%(ext)s",
        "subtitlesformat": "srt",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 找到下載的字幕檔案並重命名為 a.srt
        srt_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".srt")]
        if srt_files:
            downloaded_file = os.path.join(BASE_DIR, srt_files[0])

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

            print(f"✅ 英文字幕下載完成：{ORIGINAL_SRT}")
            return True
        else:
            print("❌ 沒有找到下載的字幕檔案")
            return False

    except Exception as e:
        print(f"❌ 字幕下載失敗：{e}")
        return False


# ===== 步驟2：翻譯字幕 =====
def translate_text(text, target_lang="zh-TW"):
    """翻譯文字"""
    if not text.strip():
        return ""
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print(f"⚠️ 翻譯失敗: {e}")
        return text


def translate_subtitles():
    """翻譯字幕"""
    print("🌐 步驟2：翻譯字幕...")

    if not os.path.exists(ORIGINAL_SRT):
        print(f"❌ 找不到原始字幕檔案: {ORIGINAL_SRT}")
        return False

    with open(ORIGINAL_SRT, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    bilingual_lines = []
    chinese_lines = []
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

    # 寫入檔案
    with open(BILINGUAL_SRT, "w", encoding="utf-8") as outfile:
        outfile.writelines(bilingual_lines)

    with open(CHINESE_SRT, "w", encoding="utf-8") as outfile:
        outfile.writelines(chinese_lines)

    print(f"\n✅ 字幕翻譯完成")

    # 調整時間軸
    adjust_subtitle_timing()

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

        bilingual_content = f"{full_text}\n{translated}\n"
        bilingual_result.extend([block_number, timecode_line, bilingual_content, "\n"])

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
    return t.strftime(TIME_FORMAT)[:-3]


def adjust_subtitle_timing():
    """調整字幕時間軸"""
    if not os.path.exists(BILINGUAL_SRT):
        return False

    with open(BILINGUAL_SRT, "r", encoding="utf-8") as f:
        content = f.read()

    blocks_raw = re.split(r"\n\s*\n", content.strip())
    blocks = []

    for block in blocks_raw:
        lines = block.splitlines()
        if len(lines) < 3:
            continue

        idx = lines[0].strip()
        times = lines[1].strip()
        en = lines[2].strip()
        zh = lines[3].strip() if len(lines) > 3 else ""

        m = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", times
        )
        if not m:
            continue

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

    return True


# ===== 步驟3：影片轉圖片 =====
def srt_time_to_seconds(srt_time):
    return (
        srt_time.hours * 3600
        + srt_time.minutes * 60
        + srt_time.seconds
        + srt_time.milliseconds / 1000
    )


def check_ffmpeg():
    """檢查 ffmpeg 是否可用"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False


def extract_images_from_video():
    """從影片中擷取圖片"""
    print("📸 步驟3：從影片中擷取圖片...")

    clean_directory(RESULT_DIR)

    if not check_ffmpeg():
        print("❌ 找不到 FFmpeg，請確認已安裝並加入 PATH")
        return False

    try:
        subs = pysrt.open(ADJUSTED_SRT, encoding="utf-8")
        print(f"📝 讀取字幕：{len(subs)} 筆")
    except Exception as e:
        print(f"❌ 讀取字幕檔失敗：{e}")
        return False

    success_count = 0

    for idx, sub in enumerate(subs, start=1):
        try:
            start = srt_time_to_seconds(sub.start)
            end = srt_time_to_seconds(sub.end)
            midpoint = (start + end) / 2

            output_file = os.path.join(RESULT_DIR, f"{idx:04d}.jpg")

            cmd = [
                "ffmpeg",
                "-ss",
                f"{midpoint:.3f}",
                "-i",
                VIDEO_PATH,
                "-frames:v",
                "1",
                "-q:v",
                "2",
                "-y",
                output_file,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and os.path.exists(output_file):
                success_count += 1
                if idx % 10 == 0:
                    print(
                        f"⏳ 擷取進度: {idx}/{len(subs)} ({(idx/len(subs))*100:.1f}%)"
                    )
            else:
                print(f"❌ 第 {idx} 張圖片擷取失敗")

        except Exception as e:
            print(f"❌ 第 {idx} 張圖片處理異常：{e}")

    print(f"✅ 圖片擷取完成：{success_count} 張")
    return success_count > 0


# ===== 步驟4：圖片加字幕 =====
def split_chinese_english(text):
    chinese = "".join(re.findall(r"[\u4e00-\u9fff，。！？；：「」、《》（）]", text))
    english = "".join(re.findall(r"[^\u4e00-\u9fff，。！？；：「」、《》（）]+", text))
    return chinese.strip(), english.strip()


def add_subtitles_to_images():
    """為圖片添加字幕"""
    print("🖼️ 步驟4：為圖片添加字幕...")

    clean_directory(RESULTX_DIR)

    try:
        subs = pysrt.open(ADJUSTED_SRT, encoding="utf-8")
    except Exception as e:
        print(f"❌ 讀取字幕檔失敗：{e}")
        return False

    img_files = sorted(
        [
            f
            for f in os.listdir(RESULT_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
    )

    if len(img_files) != len(subs):
        print(f"⚠️ 圖片數量({len(img_files)})與字幕數({len(subs)})不一致")
        min_count = min(len(img_files), len(subs))
        img_files = img_files[:min_count]
        subs = subs[:min_count]

    # 字體設定
    font_path = r"C:\Windows\Fonts\msjh.ttc"  # 微軟正黑體
    if not os.path.exists(font_path):
        font_path = r"C:\Windows\Fonts\arial.ttf"  # 備用字體

    try:
        font = ImageFont.truetype(font_path, 28)
    except:
        font = ImageFont.load_default()

    for idx, (img_file, sub) in enumerate(zip(img_files, subs), start=1):
        try:
            img_path = os.path.join(RESULT_DIR, img_file)
            img = Image.open(img_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            # 處理字幕內容
            text = sub.text.strip().replace("\n", " ")
            zh, en = split_chinese_english(text)
            lines = [en, zh] if zh and en else [text]

            # 計算文字大小
            line_sizes = []
            total_height = 0
            max_width = 0
            for line in lines:
                if line:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    line_sizes.append((line, w, h))
                    total_height += h
                    max_width = max(max_width, w)

            if not line_sizes:
                continue

            total_height += (len(line_sizes) - 1) * 10

            # 框框座標與設定
            padding = 16
            x = (img.width - max_width) / 2 - padding
            y = img.height - total_height - 40 - padding
            box_w = max_width + 2 * padding
            box_h = total_height + 2 * padding

            # 畫圓角背景框
            draw.rounded_rectangle(
                [x, y, x + box_w, y + box_h],
                radius=20,
                fill=(0, 34, 68, 200),  # 半透明藍色
            )

            # 畫每一行文字（置中）
            text_y = y + padding
            for line, w, h in line_sizes:
                text_x = (img.width - w) / 2
                draw.text((text_x, text_y), line, font=font, fill="white")
                text_y += h + 10

            # 儲存圖片
            output_path = os.path.join(RESULTX_DIR, img_file)
            img.save(output_path)

            if idx % 20 == 0:
                print(
                    f"⏳ 字幕添加進度: {idx}/{len(img_files)} ({(idx/len(img_files))*100:.1f}%)"
                )

        except Exception as e:
            print(f"❌ 處理第 {idx} 張圖片時出錯：{e}")
            continue

    print(f"✅ 字幕添加完成：{len(img_files)} 張")
    return True


# ===== 步驟5：圖片轉PDF =====
def images_to_pdf():
    """將圖片轉換為PDF"""
    print("📄 步驟5：將圖片轉換為PDF...")

    extensions = (".jpg", ".jpeg", ".png")
    img_files = sorted(
        [f for f in os.listdir(RESULTX_DIR) if f.lower().endswith(extensions)]
    )

    if not img_files:
        print("⚠️ 沒有找到圖片。")
        return False

    try:
        images = []
        for fname in img_files:
            path = os.path.join(RESULTX_DIR, fname)
            img = Image.open(path).convert("RGB")
            images.append(img)

        # 儲存為PDF
        if images:
            first_img = images[0]
            rest_imgs = images[1:] if len(images) > 1 else []
            first_img.save(FINAL_PDF, save_all=True, append_images=rest_imgs)
            print(f"✅ PDF已儲存：{FINAL_PDF}")
            return True
    except Exception as e:
        print(f"❌ PDF轉換失敗：{e}")
        return False

    return False


# ===== 主程式 =====
def main():
    """主程式"""
    print("🎬 YouTube 影片轉 PDF 整合工具")
    print("=" * 60)
    print("功能：下載影片 → 下載字幕 → 翻譯字幕 → 擷取圖片 → 添加字幕 → 生成PDF")
    print("輸出目錄：")
    print(f"  影片檔案: {VIDEO_PATH}")
    print(f"  字幕檔案: {BASE_DIR}\\[a.srt, b.srt, c.srt, d.srt]")
    print(f"  原始圖片: {RESULT_DIR}")
    print(f"  字幕圖片: {RESULTX_DIR}")
    print(f"  最終PDF: {FINAL_PDF}")
    print("=" * 60)

    # 檢查依賴
    if not check_ffmpeg():
        print("❌ 需要安裝 FFmpeg 才能使用此工具")
        print("請至 https://ffmpeg.org/ 下載並安裝")
        return

    # 獲取 YouTube 網址
    youtube_url = input("請輸入 YouTube 影片網址：").strip()
    if not youtube_url:
        print("❌ 網址不能為空！")
        return

    try:
        # 步驟1：下載影片和字幕
        if not download_youtube_video_and_subtitles(youtube_url):
            print("❌ 下載失敗，程式終止")
            return

        # 步驟2：翻譯字幕
        if not translate_subtitles():
            print("❌ 字幕翻譯失敗，程式終止")
            return

        # 步驟3：影片轉圖片
        if not extract_images_from_video():
            print("❌ 圖片擷取失敗，程式終止")
            return

        # 步驟4：圖片加字幕
        if not add_subtitles_to_images():
            print("❌ 字幕添加失敗，程式終止")
            return

        # 步驟5：圖片轉PDF
        if not images_to_pdf():
            print("❌ PDF生成失敗，程式終止")
            return

        print("\n🎉 所有步驟完成！")
        print(f"📄 最終PDF檔案：{FINAL_PDF}")

        # 顯示檔案統計
        if os.path.exists(FINAL_PDF):
            file_size = os.path.getsize(FINAL_PDF) / 1024 / 1024  # MB
            print(f"📊 PDF大小：{file_size:.2f} MB")

        img_count = len(
            [
                f
                for f in os.listdir(RESULTX_DIR)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
        )
        print(f"📊 總頁數：{img_count} 頁")

    except KeyboardInterrupt:
        print("\n⚠️ 使用者中斷操作")
    except Exception as e:
        print(f"\n❌ 程式執行出錯：{e}")


if __name__ == "__main__":
    main()
