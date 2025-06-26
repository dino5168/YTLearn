import ffmpeg

input_file = 'c:/mp3/input.wav'
output_file = 'c:/mp3/output.mp3'

ffmpeg.input(input_file).output(output_file).run()
print('ok')