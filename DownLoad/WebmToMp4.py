import ffmpeg

input_file = "C:/temp/X/my_video.webm"
output_file = "c:/temp/x/my_videoA.mp4"

ffmpeg.input(input_file).output(output_file, vcodec="libx264", acodec="aac").run()
