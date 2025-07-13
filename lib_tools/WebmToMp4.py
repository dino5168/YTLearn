import ffmpeg

input_file = "c:/temp/C/a.webm"
output_file = "c:/temp/C/a.mp4"

ffmpeg.input(input_file).output(output_file, vcodec="libx264", acodec="aac").run()
