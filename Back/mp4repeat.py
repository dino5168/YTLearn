from moviepy.editor import VideoFileClip, concatenate_videoclips

inputmp4 = r"C:\英語\Earth02.mp4"
outputmp4 = r"C:\英語\Earth02_10.mp4"
# 讀入原始 MP4 檔案
clip = VideoFileClip(inputmp4)

# 重複播放 3 次
repeated_clip = concatenate_videoclips([clip] * 5)

# 儲存為新影片
repeated_clip.write_videofile(outputmp4, codec="libx264", audio_codec="aac")
