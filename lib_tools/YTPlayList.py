from pytube import Playlist

playlist_url = (
    "https://www.youtube.com/playlist?list=PLmVd2BGjSEsg-P9a4KqHTGnZCeH7CNOlq"
)

try:
    playlist = Playlist(playlist_url)

    print(f"✅ 共有 {len(playlist.video_urls)} 部影片：\n")

    for i, url in enumerate(playlist.video_urls, start=1):
        print(f"{i}. {url}")

except Exception as e:
    print(f"❌ 無法獲取播放清單: {e}")
