import time
import random
from tqdm import tqdm
from lib_db.services.CYouTubeVideo import YouTubeVideo
from lib_db.services.CVideoManager import VideoManager


def main():
    print("🎬 批次處理 YouTube 影片資料")

    # 讀取 video_list.txt
    file_path = input("請輸入影片清單檔案名稱（預設: video_list.txt）：").strip()
    if file_path == "":
        file_path = "video_list.txt"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            video_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ 找不到檔案：{file_path}")
        return

    if not video_ids:
        print("⚠️ 清單為空，請檢查檔案內容")
        return

    # 設定選項
    download_video_input = input("是否下載影片？(y/N)：").strip().lower()
    download_video = download_video_input == "y"

    # 設定路徑
    thumbnail_dir = "c:/ytdb/thumbnails"
    srt_dir = "c:/ytdb/srt"

    # 初始化資料庫管理器
    db_manager = VideoManager()

    # 開始處理
    print(f"📥 開始處理 {len(video_ids)} 部影片...\n")

    for video_id in tqdm(video_ids, desc="處理進度", unit="部影片"):
        try:
            # 支援 ID 或完整網址
            if "http" not in video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                video_url = video_id

            youtube_video = YouTubeVideo(video_url)
            youtube_video.thumbnail_dir = thumbnail_dir
            youtube_video.srt_dir = srt_dir

            # 儲存資料、下載縮圖
            youtube_video.save_to_database(db_manager, download_thumbnail=True)

            if download_video:
                youtube_video.download()
                # youtube_video.download_subtitle()
            else:
                # youtube_video.download()
                youtube_video.download_subtitle()
                youtube_video.download_thumbnail()

        except Exception as e:
            print(f"\n⚠️ 處理影片時出錯：{video_id}\n錯誤訊息：{e}\n略過此影片。")

        # 加入隨機延遲，避免被封鎖（1~3秒）
        delay = random.uniform(10.0, 30.0)
        time.sleep(delay)

    print("\n✅ 批次處理完成！")


if __name__ == "__main__":
    main()
