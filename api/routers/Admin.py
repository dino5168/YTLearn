import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel


from lib_db.services.CYouTubeVideo import YouTubeVideo
from lib_db.services.CVideoManager import VideoManager
from lib_srt.CAdjSrt import CAdjSrt
from lib_srt.CSrtTranslator import CSrtTranslator
from lib_srt.CSrt2DB import CSrt2DB

# 讀取設定檔
from api.config import settings

YT_WATCH_URL = settings.YT_WATCH_URL
SRT_DIR = settings.SRT_DIR
BASE_DIR = settings.BASE_DIR
THUMBNAILS_DIR = settings.THUMBNAILS_DIR


# 表單輸入格式
class VideoRequest(BaseModel):
    video_id: str


admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post("/download")
async def download_video(req: VideoRequest):
    url = f"{YT_WATCH_URL}{req.video_id}"
    outputPath = f"{SRT_DIR}/{req.video_id}"
    # 依據 Video ID 建立目錄
    os.makedirs(outputPath, exist_ok=True)
    print("輸出路徑")
    print(outputPath)

    srtFile = f"{outputPath}/{req.video_id}.en.srt"
    adjFile = f"{outputPath}/{req.video_id}.adj.en.srt"
    tranfile = f"{outputPath}/{req.video_id}.srt"
    mp3filename = f"{BASE_DIR}/mp3/{req.video_id}.mp3"
    mp4filename = f"{BASE_DIR}/mp4/{req.video_id}.mp4"
    try:
        yt = YouTubeVideo(
            url,
            outputPath,
            THUMBNAILS_DIR,
            mp4filename,
            mp3filename,
        )
        yt.fetch_info()
        # yt.download_thumbnail()  # 下載縮圖
        # yt.download_subtitle()  # 下載字幕
        db = VideoManager()
        yt.save_to_database(db)
        db.close()
        # 調整字幕
        adjsrtObj = CAdjSrt(srtFile, adjFile)
        await adjsrtObj.process()
        # 翻譯
        # 基本使用
        print("翻譯成中文檔")

        translator = CSrtTranslator()
        translator.translate_file(adjFile, tranfile, "zh-TW")
        # 新增到資料庫
        processor = CSrt2DB()
        print("將字幕新增到資料庫")
        video_id = req.video_id  # 測試用影片 ID
        # 驗證檔案
        if not CSrt2DB.validate_srt_file(tranfile):
            print(f"❌ 檔案無效或不存在: {tranfile}")
        # download mp4 + mp3
        yt.download_video_with_audio()
        yt.extract_mp3_from_video()
        # 處理檔案
        success = processor.process_srt_file(tranfile, video_id)

        return {"status": "success", "video_id": req.video_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
