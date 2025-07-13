import ffmpeg

input_file = "C:\temp\0712\aa.webm"
output_file = "C:\temp\0712\aa.mp4"

ffmpeg.input(input_file).output(output_file, vcodec="libx264", acodec="aac").run()
