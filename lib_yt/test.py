# 使用範例
from CYouTubeVideo import YouTubeVideo
from lib_yt.CVideoManager import VideoManager

# 初始化資料庫管理器
db_manager = VideoManager()

video_id = "msKssRiYXVQ"
# 創建 YouTube 影片物件
video_url = f"https://www.youtube.com/watch?v={video_id}"
youtube_video = YouTubeVideo(video_url)


# 方法 1: 直接儲存到資料庫（包含下載縮圖）
video_id = youtube_video.save_to_database(db_manager, download_thumbnail=True)
# 預設路徑下載
youtube_video.thumbnail_dir = f"c:/ytdb/thumbnails"
# youtube_video.download()  # 影片下載到 c:/ytdb/srt
youtube_video.download_thumbnail()  # 縮圖下載到 c:/ytdb/thumbnails
