import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import datetime


def convert_mp3_to_wav(mp3_file):
    """Convert MP3 to WAV format for better compatibility"""
    audio = AudioSegment.from_mp3(mp3_file)
    wav_file = mp3_file.replace(".mp3", ".wav")
    audio.export(wav_file, format="wav")
    return wav_file


def split_audio_on_silence(audio_file, min_silence_len=1000, silence_thresh=-40):
    """Split audio into chunks based on silence"""
    audio = AudioSegment.from_wav(audio_file)
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,  # minimum length of silence (ms)
        silence_thresh=silence_thresh,  # silence threshold (dB)
        keep_silence=500,  # keep some silence at the beginning/end
    )
    return chunks


def transcribe_audio_chunk(chunk, recognizer, language="vi-VN"):
    """Transcribe a single audio chunk"""
    try:
        # Export chunk to temporary file
        chunk.export("temp_chunk.wav", format="wav")

        # Load the audio file
        with sr.AudioFile("temp_chunk.wav") as source:
            audio_data = recognizer.record(source)

        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Error with Google Speech Recognition: {e}")
        return ""
    finally:
        # Clean up temporary file
        if os.path.exists("temp_chunk.wav"):
            os.remove("temp_chunk.wav")


def format_time(milliseconds):
    """Convert milliseconds to SRT time format (HH:MM:SS,mmm)"""
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")


def create_srt_file(transcriptions, output_file):
    """Create SRT subtitle file from transcriptions"""
    with open(output_file, "w", encoding="utf-8") as f:
        subtitle_index = 1
        current_time = 0

        for i, (text, duration) in enumerate(transcriptions):
            if text.strip():  # Only add non-empty transcriptions
                start_time = format_time(current_time)
                end_time = format_time(current_time + duration)

                f.write(f"{subtitle_index}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

                subtitle_index += 1

            current_time += duration


def mp3_to_srt(mp3_file, output_srt=None, language="vi-VN"):
    """Main function to convert MP3 to SRT"""
    if output_srt is None:
        output_srt = mp3_file.replace(".mp3", ".srt")

    print("Converting MP3 to WAV...")
    wav_file = convert_mp3_to_wav(mp3_file)

    print("Splitting audio into chunks...")
    chunks = split_audio_on_silence(wav_file)

    print(f"Found {len(chunks)} audio chunks")
    print("Transcribing audio chunks...")

    recognizer = sr.Recognizer()
    transcriptions = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        text = transcribe_audio_chunk(chunk, recognizer, language)
        duration = len(chunk)  # Duration in milliseconds
        transcriptions.append((text, duration))

    print("Creating SRT file...")
    create_srt_file(transcriptions, output_srt)

    # Clean up temporary WAV file
    if os.path.exists(wav_file):
        os.remove(wav_file)

    print(f"SRT file created: {output_srt}")


# Alternative method using longer audio segments for better accuracy
def mp3_to_srt_segments(
    mp3_file, segment_duration=30000, output_srt=None, language="vi-VN"
):
    """Convert MP3 to SRT using fixed-duration segments"""
    if output_srt is None:
        output_srt = mp3_file.replace(".mp3", ".srt")

    print("Converting MP3 to WAV...")
    wav_file = convert_mp3_to_wav(mp3_file)

    print("Loading audio...")
    audio = AudioSegment.from_wav(wav_file)
    total_duration = len(audio)

    recognizer = sr.Recognizer()
    transcriptions = []

    current_pos = 0
    segment_num = 1

    while current_pos < total_duration:
        end_pos = min(current_pos + segment_duration, total_duration)
        segment = audio[current_pos:end_pos]

        print(
            f"Processing segment {segment_num} ({current_pos/1000:.1f}s - {end_pos/1000:.1f}s)..."
        )

        # Export segment to temporary file
        segment.export("temp_segment.wav", format="wav")

        try:
            with sr.AudioFile("temp_segment.wav") as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data, language=language)
            transcriptions.append((text, segment_duration))
            print(f"Transcribed: {text[:50]}...")

        except sr.UnknownValueError:
            transcriptions.append(("", segment_duration))
            print("No speech detected in this segment")
        except sr.RequestError as e:
            print(f"Error: {e}")
            transcriptions.append(("", segment_duration))

        # Clean up temporary file
        if os.path.exists("temp_segment.wav"):
            os.remove("temp_segment.wav")

        current_pos = end_pos
        segment_num += 1

    print("Creating SRT file...")
    create_srt_file(transcriptions, output_srt)

    # Clean up temporary WAV file
    if os.path.exists(wav_file):
        os.remove(wav_file)

    print(f"SRT file created: {output_srt}")


# Example usage
if __name__ == "__main__":
    # Replace with your MP3 file path
    mp3_file_path = r"C:\temp\my_audio.mp3"

    # Method 1: Split on silence (better for natural speech)
    print("Method 1: Split on silence")
    mp3_to_srt(mp3_file_path, language="vi-VN")

    # Method 2: Fixed segments (more reliable timing)
    # print("Method 2: Fixed segments")
    # mp3_to_srt_segments(mp3_file_path, segment_duration=20000, language='vi-VN')
