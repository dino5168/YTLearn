from FasterWhisperTranscriber import FasterWhisperTranscriber

if __name__ == "__main__":
    input_audio = "c:/temp/0719/1.mp3"
    output_srt = "c:/temp/0719/1.srt"

    transcriber = FasterWhisperTranscriber(model_size="small")
    transcriber.transcribe_to_srt(input_audio, output_srt)
