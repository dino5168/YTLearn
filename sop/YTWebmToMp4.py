import ffmpeg

input_file = "c:/temp/my_video.webm"
output_file = "c:/temp/my_videoA.mp4"

ffmpeg.input(input_file).output(output_file, vcodec="libx264", acodec="aac").run()
