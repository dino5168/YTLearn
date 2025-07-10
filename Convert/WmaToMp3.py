import os
import subprocess


def convert_wma_to_mp3_ffmpeg(input_path: str, output_path: str):
    cmd = [
        "ffmpeg",
        "-y",  # 自動覆蓋檔案（避免詢問）
        "-i",
        input_path,
        "-codec:a",
        "libmp3lame",
        "-q:a",
        "2",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ 已轉檔：{output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 轉檔失敗：{input_path}\n錯誤訊息：{e.stderr.decode('utf-8')}")


def batch_convert_wma_in_folder(folder_path: str):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".wma"):
            wma_path = os.path.join(folder_path, filename)
            mp3_filename = os.path.splitext(filename)[0] + ".mp3"
            mp3_path = os.path.join(folder_path, mp3_filename)
            convert_wma_to_mp3_ffmpeg(wma_path, mp3_path)


# ✅ 使用方式：指定資料夾
batch_convert_wma_in_folder(r"C:\temp\b")
