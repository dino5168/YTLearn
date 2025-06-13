# 很爛 不要用
import os
import math
import wave
import contextlib
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence


def get_audio_duration(audio_path):
    with contextlib.closing(wave.open(audio_path, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def convert_to_wav(audio_path):
    audio = AudioSegment.from_file(audio_path)
    wav_path = os.path.splitext(audio_path)[0] + "._converted.wav"
    audio.export(wav_path, format="wav")
    duration = get_audio_duration(wav_path)
    return wav_path, duration


def split_audio_by_duration(audio_path, chunk_duration=30):
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_duration * 1000):
        chunk = audio[i : i + chunk_duration * 1000]
        chunks.append(chunk)
    return chunks


def split_audio_by_silence_with_times(
    audio_path, min_silence_len=1000, silence_thresh=-40
):
    audio = AudioSegment.from_wav(audio_path)
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=500,
    )

    chunk_times = []
    cursor = 0
    for chunk in chunks:
        start = cursor
        end = start + len(chunk)
        chunk_times.append((start / 1000.0, end / 1000.0))
        cursor = end
    return chunks, chunk_times


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def generate_srt(segments, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            f.write(f"{i + 1}\n")
            f.write(
                f"{format_time(segment['start'])} --> {format_time(segment['end'])}\n"
            )
            f.write(f"{segment['text']}\n\n")


def transcribe_audio(audio_path, language="zh-TW", split_mode=1):
    recognizer = sr.Recognizer()
    wav_path, total_duration = convert_to_wav(audio_path)
    if not wav_path:
        return []

    try:
        if split_mode == 2:
            chunks = split_audio_by_duration(wav_path, 30)
            chunk_times = []
            for i, chunk in enumerate(chunks):
                start = i * 30.0
                end = start + len(chunk) / 1000.0
                chunk_times.append((start, end))
        else:
            chunks, chunk_times = split_audio_by_silence_with_times(wav_path)

        if not chunks:
            print("音訊分割失敗，嘗試整個檔案轉錄...")
            audio = AudioSegment.from_wav(wav_path)
            chunks = [audio]
            chunk_times = [(0, len(audio) / 1000.0)]

        print(f"共分割成 {len(chunks)} 個片段")
        segments = []
        for i, (chunk, (start_sec, end_sec)) in enumerate(zip(chunks, chunk_times)):
            print(f"正在處理片段 {i+1}/{len(chunks)}...")
            chunk_path = f"temp_chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")
            try:
                with sr.AudioFile(chunk_path) as source:
                    audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language=language)
                    segments.append({"start": start_sec, "end": end_sec, "text": text})
                    print(f"  ✓ 片段 {i+1}: {text[:50]}...")
                except sr.UnknownValueError:
                    print(f"  ✗ 無法辨識片段 {i+1}")
                except sr.RequestError as e:
                    print(f"  ✗ Google API 錯誤: {e}")
            except Exception as e:
                print(f"  ✗ 錯誤處理片段 {i+1}: {e}")
            finally:
                try:
                    os.remove(chunk_path)
                except:
                    pass
        return segments
    finally:
        try:
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("請提供音訊檔案路徑，例如：python transcribe.py your_audio.mp3")
        sys.exit(1)

    audio_file = sys.argv[1]
    output_srt = os.path.splitext(audio_file)[0] + ".srt"

    segments = transcribe_audio(audio_file, language="zh-TW", split_mode=1)
    generate_srt(segments, output_srt)
    print(f"已輸出字幕檔至 {output_srt}")
