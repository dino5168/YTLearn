import whisper
import os
import sys
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    """將秒數轉換為 SRT 格式的時間戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments, file_path):
    """將轉錄結果寫入 SRT 字幕檔"""
    try:
        # 確保輸出目錄存在
        output_dir = Path(file_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        return True
    except Exception as e:
        print(f"寫入 SRT 檔案時發生錯誤：{e}")
        return False


def get_model_name():
    """取得使用者選擇的模型名稱"""
    valid_models = ["tiny", "base", "small", "medium", "large"]

    print("可用的 Whisper 模型：")
    for i, model in enumerate(valid_models, 1):
        print(f"{i}. {model}")

    while True:
        choice = input("請選擇模型 (1-5) 或直接輸入模型名稱 [預設: base]：").strip()

        if not choice:  # 空輸入，使用預設
            return "base"

        # 如果是數字選擇
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(valid_models):
                return valid_models[idx]

        # 如果是直接輸入模型名稱
        if choice.lower() in valid_models:
            return choice.lower()

        print("輸入無效，請重新選擇。")


def get_audio_path():
    """取得音訊檔案路徑並驗證"""
    while True:
        audio_path = input("請輸入音訊檔案的完整路徑：").strip().strip('"')

        if not audio_path:
            print("路徑不能為空，請重新輸入。")
            continue

        if not os.path.exists(audio_path):
            print(f"檔案不存在：{audio_path}")
            continue

        # 檢查是否為支援的音訊格式
        supported_formats = [
            ".mp3",
            ".wav",
            ".m4a",
            ".flac",
            ".ogg",
            ".mp4",
            ".avi",
            ".mov",
        ]
        file_ext = Path(audio_path).suffix.lower()

        if file_ext not in supported_formats:
            print(f"不支援的檔案格式：{file_ext}")
            print(f"支援的格式：{', '.join(supported_formats)}")
            continue

        return audio_path


def get_output_path(audio_path):
    """取得輸出 SRT 檔案路徑"""
    # 預設輸出路徑（與音訊檔案同目錄，同檔名）
    default_output = str(Path(audio_path).with_suffix(".srt"))

    output_path = (
        input(f"請輸入輸出 SRT 檔案路徑 [預設: {default_output}]：").strip().strip('"')
    )

    if not output_path:
        output_path = default_output

    # 確保副檔名為 .srt
    if not output_path.lower().endswith(".srt"):
        output_path += ".srt"

    return output_path


def get_language():
    """取得語言設定"""
    languages = {
        "1": ("zh", "中文"),
        "2": ("en", "英文"),
        "3": ("ja", "日文"),
        "4": ("ko", "韓文"),
        "5": (None, "自動偵測"),
    }

    print("\n語言選項：")
    for key, (code, name) in languages.items():
        print(f"{key}. {name}")

    while True:
        choice = input("請選擇語言 (1-5) [預設: 1-中文]：").strip()

        if not choice:
            return "zh"

        if choice in languages:
            return languages[choice][0]

        print("輸入無效，請重新選擇。")


def main():
    print("=== Whisper 音訊轉字幕程式 ===\n")

    try:
        # 取得使用者輸入
        model_name = get_model_name()
        audio_path = get_audio_path()
        output_path = get_output_path(audio_path)
        language = get_language()

        # 載入模型
        print(f"\n載入模型：{model_name}...")
        try:
            model = whisper.load_model(model_name)
        except Exception as e:
            print(f"載入模型失敗：{e}")
            return

        # 執行轉錄
        print("開始轉錄音訊...")
        print("這可能需要一些時間，請耐心等待...")

        try:
            if language:
                result = model.transcribe(audio_path, language=language)
            else:
                result = model.transcribe(audio_path)
        except Exception as e:
            print(f"轉錄過程中發生錯誤：{e}")
            return

        # 輸出 SRT
        print("正在產生字幕檔...")
        if write_srt(result["segments"], output_path):
            print(f"✓ 轉錄完成！字幕檔已儲存至：{output_path}")

            # 顯示統計資訊
            total_segments = len(result["segments"])
            total_duration = result.get("duration", 0)
            print(f"  - 總共 {total_segments} 個字幕段落")
            print(f"  - 音訊總長度：{format_timestamp(total_duration)}")

            # 偵測到的語言
            detected_language = result.get("language", "未知")
            print(f"  - 偵測到的語言：{detected_language}")
        else:
            print("✗ 字幕檔產生失敗")

    except KeyboardInterrupt:
        print("\n\n程式被使用者中斷")
    except Exception as e:
        print(f"程式執行時發生未預期的錯誤：{e}")


if __name__ == "__main__":
    main()
