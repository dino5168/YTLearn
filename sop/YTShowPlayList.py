from yt_dlp import YoutubeDL


def get_playlist_video_urls(playlist_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,  # 只取得清單，不深入解析
        "force_generic_extractor": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(playlist_url, download=False)
        entries = info_dict.get("entries", [])

        video_urls = [entry["url"] for entry in entries if "url" in entry]
        return video_urls


def save_playlist_files(video_ids, filename_prefix="playlist"):
    # 建立 playlist01.txt（完整連結）
    with open(f"{filename_prefix}01.txt", "w", encoding="utf-8") as f1:
        for i, vid in enumerate(video_ids, 1):
            f1.write(f"{i}. https://www.youtube.com/watch?v={vid}\n")

    # 建立 playlist02.txt（只有 video ID）
    with open(f"{filename_prefix}02.txt", "w", encoding="utf-8") as f2:
        for vid in video_ids:
            f2.write(f"{vid}\n")


def main():
    playlist_url = input("請輸入 YouTube 播放清單網址：\n> ").strip()
    print("📥 正在擷取播放清單影片 ID...")

    try:
        video_ids = get_playlist_video_urls(playlist_url)
        print(f"✅ 成功擷取 {len(video_ids)} 部影片")
        save_playlist_files(video_ids)
        print("📄 已輸出 playlist01.txt（原始資料）、playlist02.txt（只有影片 ID）")
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")


if __name__ == "__main__":
    main()
