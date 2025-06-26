# 使用範例
from CYouTubeVideo import YouTubeVideo
from lib_yt.CVideoManager import VideoManager

# 初始化資料庫管理器
db_manager = VideoManager()

video_id = "dQw4w9WgXcQ"
# 創建 YouTube 影片物件
video_url = f"https://www.youtube.com/watch?v={video_id}"
youtube_video = YouTubeVideo(video_url)

# 方法 1: 直接儲存到資料庫（包含下載縮圖）
video_id = youtube_video.save_to_database(db_manager, download_thumbnail=True)

# 方法 2: 先取得資訊，再手動儲存
youtube_video.fetch_info()
video_data = youtube_video.to_database_format()
db_manager.add_or_update_video(video_data)

# 方法 3: 批量處理多個影片
video_urls = [
    "https://www.youtube.com/watch?v=video1",
    "https://www.youtube.com/watch?v=video2",
    "https://www.youtube.com/watch?v=video3",
]

for url in video_urls:
    try:
        video = YouTubeVideo(url)
        video.save_to_database(db_manager, download_thumbnail=True)
    except Exception as e:
        print(f"處理影片 {url} 時發生錯誤: {e}")

# 從資料庫中查詢影片
stored_video = db_manager.get_video(video_id)
if stored_video:
    print(f"從資料庫取得的影片標題: {stored_video['title']}")

# 關閉資料庫連接
db_manager.close()
