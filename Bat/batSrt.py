from whisper_transcriber import transcribe_to_srt
import os

# 互動輸入路徑
input_folder = input("請輸入音訊檔案資料夾路徑（例如 C:\\temp\\佛教故事\\mp3）：")
output_folder = input("請輸入字幕輸出資料夾路徑（例如 C:\\temp\\佛教故事\\srt）：")

# 確保輸出資料夾存在
os.makedirs(output_folder, exist_ok=True)

files = os.listdir(input_folder)
for file_name in files:
    if file_name.endswith(".mp3"):
        audio_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(
            output_folder, f"{os.path.splitext(file_name)[0]}.srt"
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
