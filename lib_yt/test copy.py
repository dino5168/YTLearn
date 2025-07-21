from Whisper.FasterWhisperTranscriber import FasterWhisperTranscriber
from YTHandler.YouTubeHandler import YouTubeHandler
import re
import os
from datetime import timedelta
from YTTrans import process_srt
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ✅ 連線設定（注意：要用 asyncpg driver）
DB_CONNECT_STRING = "postgresql+asyncpg://postgres:0936284791@localhost:5432/videos"

# ✅ 建立 async engine
engine = create_async_engine(DB_CONNECT_STRING, echo=True)

# ✅ 建立 Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


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


async def insert_ytinfo():
    async with AsyncSessionLocal() as session:
        # ✅ 查詢資料
        result = await session.execute(text("SELECT id, name, email FROM users"))

        # ✅ 使用 result.mappings() 取得 dict-like 結果（推薦）
        for row in result.mappings():
            print(f"查詢結果: {row['id']}, {row['name']}, {row['email']}")


async def main():

    await insert_ytinfo()
    url = input("請輸入 YouTube 影片網址: ")
    output_dir = input("請輸入儲存資料夾路徑 (預設 C:/temp): ") or "C:/temp"

    try:
        handler = YouTubeHandler(url, output_dir)

        # 方法1: 分別執行
        # video_info = handler.fetch_video_info()
        # output_vedio_path = os.path.join(output_dir,video_info.category,video_info.video_id)
        # os.makedirs(output_vedio_path,exist_ok=True)
        # audio_path = handler.download_audio()
        # thumbnail_path = handler.download_thumbnail()

        # 方法2: 一次性處理
        video_info, audio_path, thumbnail_path = handler.process_video()

        print(f"\n✨ 處理結果:")
        # print(f"📄 影片資訊: {video_info.title}")
        # print(f"🎵 音訊檔案: {audio_path}")
        # print(f"🖼 封面圖片: {thumbnail_path}")

    except Exception as e:
        print(f"💥 發生錯誤: {e}")
    #
    #
    base_path = "c:/temp/0721"
    output_path = f"{base_path}/{video_info.category}/{video_info.video_id}"
    mp3_file_name = f"{output_path}/{video_info.video_id}.mp3"
    srt_file_name = f"{output_path}/{video_info.video_id}.srt"
    srt_en_file_name = f"{output_path}/{video_info.video_id}.en.srt"
    # 翻譯好的 字幕檔。
    srt_2_file_name = f"{output_path}/{video_info.video_id}.2.srt"
    trans = FasterWhisperTranscriber()
    trans_result = trans.transcribe_to_srt(mp3_file_name, srt_file_name)
    print(trans_result)

    merge_srt_to_sentence_srt(srt_file_name, srt_en_file_name)
    # 翻譯
    process_srt(srt_file_name, srt_2_file_name, "zh-TW")
    # 將資料寫入資料庫


if __name__ == "__main__":
    asyncio.run(main())
    # 將結果 寫入資料庫
