import sys
import os
import re

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy.orm import Session
from lib_db.db.database_lite import SessionLocal
from lib_db.schemas.Subtitle import SubtitleCreate

# 正確的匯入方式：匯入具體的函數
from lib_db.crud.subtitle_crud import create_subtitle


def parse_srt_file(filepath: str, video_id: str) -> list[SubtitleCreate]:
    with open(filepath, encoding="utf-8") as f:
        srt_content = f.read()

    blocks = re.split(r"\n\s*\n", srt_content.strip())
    subtitles = []

    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue

        try:
            seq = int(lines[0].strip())
            times = lines[1].split(" --> ")
            start_time = times[0].strip()
            end_time = times[1].strip()

            text_lines = lines[2:]
            en_text = ""
            zh_text = ""

            for line in text_lines:
                # 簡單判斷中英文：可根據需求自訂
                if re.search(r"[\u4e00-\u9fff]", line):
                    zh_text += line.strip() + " "
                else:
                    en_text += line.strip() + " "

            subtitles.append(
                SubtitleCreate(
                    video_id=video_id,
                    seq=seq,
                    start_time=start_time,
                    end_time=end_time,
                    en_text=en_text.strip(),
                    zh_text=zh_text.strip(),
                )
            )
        except Exception as e:
            print(f"⚠️ 解析錯誤: {e}, block: {block}")
            continue

    return subtitles


def insert_subtitles_to_db(subtitles: list[SubtitleCreate]):
    db: Session = SessionLocal()
    try:
        # 方法 1: 逐個插入
        for sub in subtitles:
            create_subtitle(db, sub)
        print(f"✅ 插入完成，共 {len(subtitles)} 筆")

        # 方法 2: 批量插入 (更有效率)
        # bulk_create_subtitles(db, subtitles)
        # print(f"✅ 批量插入完成，共 {len(subtitles)} 筆")

    except Exception as e:
        print(f"❌ 插入失敗: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    srt_file_path = f"c:\ytdb\srt\8WUs79OQgFQ.tw.en.srt"  # 你的字幕檔案路徑
    video_id = "8WUs79OQgFQ"  # 測試用影片 ID

    print(f"📖 開始解析字幕檔案: {srt_file_path}")
    subtitles = parse_srt_file(srt_file_path, video_id)
    print(f"📝 解析完成，共 {len(subtitles)} 筆字幕")

    if subtitles:
        insert_subtitles_to_db(subtitles)
    else:
        print("⚠️ 沒有找到任何字幕資料")
