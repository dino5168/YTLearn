import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel


from lib_db.models.User import User
from lib_db.services.CYouTubeVideo import YouTubeVideo
from lib_db.services.CVideoManager import VideoManager
from lib_srt.CAdjSrt import CAdjSrt
from lib_srt.CSrtTranslator import CSrtTranslator
from lib_srt.CSrt2DB import CSrt2DB
from lib_util.Auth import get_current_user
from lib_yt.Whisper import FasterWhisperTranscriber
from lib_yt.YTHandler.YTInfo import fetch_info, save_video_to_db, query_video_byid
from lib_yt.YTHandler.refine_srt_sentences import refine

# 讀取設定檔
from app.config import settings
from lib_yt.YTHandler.YTMp3 import (
    download_mp3_from_info,
    download_thumbnail_from_info,
    process_srt,
    transcribe_mp3_to_srt,
)
from lib_yt.YTHandler.YouTubeHandler import YouTubeHandler

YT_WATCH_URL = settings.YT_WATCH_URL
SRT_DIR = settings.SRT_DIR
BASE_DIR = settings.BASE_DIR
THUMBNAILS_DIR = settings.THUMBNAILS_DIR


# 表單輸入格式
class VideoRequest(BaseModel):
    video_id: str


admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post("/download")
async def download_video(
    req: VideoRequest, current_user: User = Depends(get_current_user)
):
    output_dir = "C:/temp/0721"
    video_id = req.video_id
    url = f"{YT_WATCH_URL}{video_id}"
    print(current_user["id"])
    print(url)
    query_result = await query_video_byid(video_id)
    if query_result:
        return {"status": "資料已經存在", "video_id": video_id}
    # 存到資料庫

    # print(query_result.category)
    info = await fetch_info(url)
    video = await save_video_to_db(info, current_user["id"])
    output_dir = os.path.join(output_dir, video_id)
    os.makedirs(output_dir, exist_ok=True)
    # 下載 mp3
    await download_mp3_from_info(info, output_dir)
    # 下載封面
    print("下載封面")

    await download_thumbnail_from_info(info, output_dir)
    # 產生字幕
    mp3_file_name = f"{output_dir}/{video_id}.mp3"
    # mp3_source_srt = f"{output_dir}/{video_id}.0.srt"
    srt_file_name = f"{output_dir}/{video_id}.srt"

    await transcribe_mp3_to_srt(mp3_file_name, srt_file_name)
    # 調整字幕
    # refine(mp3_source_srt, srt_file_name)
    # 產生翻譯字幕
    srt_2_file_name = f"{output_dir}/{video_id}.2.srt"

    await process_srt(srt_file_name, srt_2_file_name, "zh-TW")
    # 新增到資料庫
    processor = CSrt2DB()
    print("將字幕新增到資料庫")
    # 驗證檔案
    if not CSrt2DB.validate_srt_file(srt_2_file_name):
        print(f"❌ 檔案無效或不存在: {srt_2_file_name}")
    # 將字幕檔新增到資料庫
    success = processor.process_srt_file(srt_2_file_name, video_id)

    # 處理檔案

    return {"status": "success", "video_id": req.video_id}


@admin_router.post("/download_0721")
async def download_video_0721(req: VideoRequest):
    url = f"{YT_WATCH_URL}{req.video_id}"
    outputPath = f"{SRT_DIR}/{req.video_id}"

    # 依據 Video ID 建立目錄
    os.makedirs(outputPath, exist_ok=True)
    # print("輸出路徑")
    # print(outputPath)

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
