import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy.orm import Session
from lib_db.db.database import SessionLocal
from lib_db.crud.subtitle_crud import get_subtitles_by_video


def test_get_subtitles_by_video(video_id: str):
    """測試獲取指定影片的所有字幕"""
    db: Session = SessionLocal()

    try:
        print(f"🔍 正在查詢影片 '{video_id}' 的字幕...")

        # 獲取字幕列表
        subtitles = get_subtitles_by_video(db, video_id)

        print(f"📊 找到 {len(subtitles)} 筆字幕記錄")

        if not subtitles:
            print("❌ 沒有找到任何字幕記錄")
            return

        print("\n" + "=" * 80)
        print(f"影片 ID: {video_id}")
        print("=" * 80)

        # 顯示字幕詳細資訊
        for i, subtitle in enumerate(subtitles[:10]):  # 只顯示前10筆，避免輸出太多
            print(f"\n📝 字幕 #{subtitle.seq} (ID: {subtitle.id})")
            print(f"   時間: {subtitle.start_time} --> {subtitle.end_time}")
            if subtitle.en_text.strip():
                print(
                    f"   英文: {subtitle.en_text[:100]}{'...' if len(subtitle.en_text) > 100 else ''}"
                )
            if subtitle.zh_text.strip():
                print(
                    f"   中文: {subtitle.zh_text[:100]}{'...' if len(subtitle.zh_text) > 100 else ''}"
                )

        if len(subtitles) > 10:
            print(f"\n... 還有 {len(subtitles) - 10} 筆記錄未顯示")

        # 統計資訊
        print(f"\n📈 統計資訊:")
        print(f"   總字幕數: {len(subtitles)}")

        en_count = sum(1 for s in subtitles if s.en_text.strip())
        zh_count = sum(1 for s in subtitles if s.zh_text.strip())

        print(f"   有英文字幕: {en_count} 筆")
        print(f"   有中文字幕: {zh_count} 筆")

        if subtitles:
            print(f"   第一筆時間: {subtitles[0].start_time}")
            print(f"   最後一筆時間: {subtitles[-1].end_time}")

    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
        raise
    finally:
        db.close()


def test_multiple_videos():
    """測試多個影片的字幕查詢"""
    test_video_ids = [
        "jKi2SvWOCXc",
    ]

    print("🎬 測試多個影片的字幕查詢...")

    for video_id in test_video_ids:
        db: Session = SessionLocal()
        try:
            subtitles = get_subtitles_by_video(db, video_id)
            print(f"📹 {video_id}: {len(subtitles)} 筆字幕")
        except Exception as e:
            print(f"📹 {video_id}: 查詢失敗 - {e}")
        finally:
            db.close()


if __name__ == "__main__":
    print("🚀 字幕查詢功能測試")
    print("=" * 50)

    # 測試 1: 基本查詢測試
    print("\n1️⃣ 基本查詢測試")
    test_video_id = "jKi2SvWOCXc"  # 使用您之前插入的影片 ID
    test_get_subtitles_by_video(test_video_id)

    print("\n✅ 所有測試完成！")
