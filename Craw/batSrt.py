from whisper_transcriber import transcribe_to_srt
import os

files = os.listdir(r"C:\temp\佛教故事\mp3")
for file_name in files:
    if file_name.endswith(".mp3"):
        audio_path = os.path.join(r"C:\temp\佛教故事\mp3", file_name)
        # 確保輸出路徑存在
        output_path = os.path.join(
            r"C:\temp\佛教故事\srt", f"{os.path.splitext(file_name)[0]}.srt"
        )
        print(f"正在處理文件: {audio_path}")
        success = transcribe_to_srt(
            audio_path=audio_path,
            output_path=output_path,
            model_name="medium",
            language="zh",
        )
        if success:
            print("字幕生成成功！")
        else:
            print("字幕生成失敗。")
