import sys
import os
import re
from typing import List, Optional

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy.orm import Session
from lib_db.db.database import SessionLocal
from lib_db.schemas.Subtitle import SubtitleCreate
from lib_db.crud.subtitle_crud import create_subtitle


class CSrt2DB:
    """字幕處理器類，負責解析SRT檔案並插入到資料庫"""

    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化字幕處理器

        Args:
            db_session: 可選的資料庫會話，如果不提供則使用預設的SessionLocal
        """
        self.db_session = db_session

    def parse_srt_file(self, filepath: str, video_id: str) -> List[SubtitleCreate]:
        """
        解析SRT字幕檔案

        Args:
            filepath: SRT檔案路徑
            video_id: 影片ID

        Returns:
            SubtitleCreate物件列表
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                srt_content = f.read()
        except FileNotFoundError:
            print(f"❌ 檔案不存在: {filepath}")
            return []
        except Exception as e:
            print(f"❌ 讀取檔案失敗: {e}")
            return []

        blocks = re.split(r"\n\s*\n", srt_content.strip())
        subtitles = []

        for block in blocks:
            subtitle = self._parse_subtitle_block(block, video_id)
            if subtitle:
                subtitles.append(subtitle)

        return subtitles

    def _parse_subtitle_block(
        self, block: str, video_id: str
    ) -> Optional[SubtitleCreate]:
        """
        解析單個字幕區塊

        Args:
            block: 字幕區塊文字
            video_id: 影片ID

        Returns:
            SubtitleCreate物件或None
        """
        lines = block.strip().splitlines()
        if len(lines) < 3:
            return None

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

            return SubtitleCreate(
                video_id=video_id,
                seq=seq,
                start_time=start_time,
                end_time=end_time,
                en_text=en_text.strip(),
                zh_text=zh_text.strip(),
            )
        except Exception as e:
            print(f"⚠️ 解析錯誤: {e}, block: {block}")
            return None

    def insert_subtitles_to_db(self, subtitles: List[SubtitleCreate]) -> bool:
        """
        將字幕插入到資料庫

        Args:
            subtitles: SubtitleCreate物件列表

        Returns:
            插入是否成功
        """
        if not subtitles:
            print("⚠️ 沒有字幕資料需要插入")
            return False

        # 使用提供的會話或創建新的會話
        db = self.db_session or SessionLocal()
        should_close_db = self.db_session is None

        try:
            # 逐個插入
            for sub in subtitles:
                create_subtitle(db, sub)
            print(f"✅ 插入完成，共 {len(subtitles)} 筆")
            return True

        except Exception as e:
            print(f"❌ 插入失敗: {e}")
            return False
        finally:
            if should_close_db:
                db.close()

    def process_srt_file(self, filepath: str, video_id: str) -> bool:
        """
        完整處理SRT檔案：解析並插入資料庫

        Args:
            filepath: SRT檔案路徑
            video_id: 影片ID

        Returns:
            處理是否成功
        """
        print(f"📖 開始解析字幕檔案: {filepath}")

        subtitles = self.parse_srt_file(filepath, video_id)
        print(f"📝 解析完成，共 {len(subtitles)} 筆字幕")

        if not subtitles:
            print("⚠️ 沒有找到任何字幕資料")
            return False

        return self.insert_subtitles_to_db(subtitles)

    @staticmethod
    def validate_srt_file(filepath: str) -> bool:
        """
        驗證SRT檔案是否存在且可讀取

        Args:
            filepath: 檔案路徑

        Returns:
            檔案是否有效
        """
        return os.path.isfile(filepath) and os.access(filepath, os.R_OK)


# 使用範例
if __name__ == "__main__":
    # 方法1: 使用預設資料庫會話
    processor = CSrt2DB()

    srt_file_path = r"c:\ytdb\srt\8WUs79OQgFQ.tw.en.srt"  # 你的字幕檔案路徑
    video_id = "8WUs79OQgFQ"  # 測試用影片 ID

    # 驗證檔案
    if not CSrt2DB.validate_srt_file(srt_file_path):
        print(f"❌ 檔案無效或不存在: {srt_file_path}")
        sys.exit(1)

    # 處理檔案
    success = processor.process_srt_file(srt_file_path, video_id)

    if success:
        print("🎉 字幕處理完成！")
    else:
        print("❌ 字幕處理失敗！")

    # 方法2: 使用自定義資料庫會話
    # db_session = SessionLocal()
    # try:
    #     processor = SubtitleProcessor(db_session)
    #     success = processor.process_srt_file(srt_file_path, video_id)
    # finally:
    #     db_session.close()
