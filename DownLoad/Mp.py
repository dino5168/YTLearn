import ffmpeg


def extract_audio(webm_path: str, output_mp3_path: str):
    (
        ffmpeg.input(webm_path)
        .output(output_mp3_path, format="mp3", acodec="libmp3lame")
        .run(overwrite_output=True)
    )


# 使用範例
extract_audio(r"C:\temp\X\my_video.webm", r"C:\temp\X\my_video.mp3")
