import whisper
from pathlib import Path
import sys
import os
from typing import Optional, List


def format_timestamp(seconds: float) -> str:
    """格式化時間戳記為 SRT 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments, file_path: str) -> bool:
    """將轉錄結果寫入 SRT 檔案"""
    try:
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
        print(f"❌ 寫入 SRT 發生錯誤：{e}")
        return False


def get_available_models() -> List[str]:
    """取得可用的 Whisper 模型"""
    return ["tiny", "base", "small", "medium", "large"]


def get_supported_languages() -> dict:
    """取得支援的語言代碼"""
    return {
        "en": "English",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ar": "Arabic",
        "hi": "Hindi",
        "auto": "自動偵測",
    }


def validate_audio_file(file_path: str) -> bool:
    """驗證音訊檔案是否存在且為支援格式"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ 檔案不存在：{file_path}")
        return False

    supported_formats = {
        ".mp3",
        ".wav",
        ".m4a",
        ".flac",
        ".ogg",
        ".opus",
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
    }
    if path.suffix.lower() not in supported_formats:
        print(f"⚠️  警告：檔案格式 {path.suffix} 可能不受支援")
        print(f"   支援格式：{', '.join(supported_formats)}")
        return input("是否繼續？(y/N): ").lower() == "y"

    return True


def transcribe_to_srt(
    audio_path: str,
    output_path: Optional[str] = None,
    model_name: str = "base",
    language: str = "en",
) -> bool:
    """
    將音訊轉錄為字幕（SRT），並儲存至指定檔案。

    參數:
        audio_path: 音訊檔案路徑
        output_path: 輸出 SRT 路徑（可選）
        model_name: Whisper 模型名稱（tiny/base/small/medium/large）
        language: 指定語言代碼（例如 "zh", "en", "auto"）

    回傳:
        成功為 True，失敗為 False
    """
    audio_path = Path(audio_path)

    if not validate_audio_file(str(audio_path)):
        return False

    if output_path is None:
        output_path = str(audio_path.with_suffix(".srt"))

    print(f"📂 音訊檔案：{audio_path}")
    print(f"📝 輸出檔案：{output_path}")
    print(f"🤖 使用模型：{model_name}")
    print(f"🌐 指定語言：{language}")
    print("-" * 50)

    try:
        print("🔄 載入模型中...")
        model = whisper.load_model(model_name)
        print("✅ 模型載入成功")
    except Exception as e:
        print(f"❌ 載入模型失敗：{e}")
        return False

    try:
        print("🎵 開始轉錄...")
        transcribe_params = {"verbose": True}
        if language != "auto":
            transcribe_params["language"] = language

        result = model.transcribe(str(audio_path), **transcribe_params)
        print("✅ 轉錄完成")
    except Exception as e:
        print(f"❌ 轉錄失敗：{e}")
        return False

    success = write_srt(result["segments"], output_path)
    if success:
        print(f"✅ 字幕已儲存：{output_path}")
        print(f"   🔍 偵測語言：{result.get('language', '未知')}")
        print(f"   ⏱️  音訊長度：{format_timestamp(result.get('duration', 0))}")
        print(f"   📊 字幕片段數：{len(result['segments'])}")

    return success


def interactive_mode():
    """交談式模式"""
    print("🎤 Whisper 音訊轉錄工具")
    print("=" * 50)

    while True:
        print("\n📁 請輸入音訊檔案路徑（或 'q' 退出）:")
        audio_path = input(">>> ").strip()

        if audio_path.lower() in ["q", "quit", "exit"]:
            print("👋 再見！")
            break

        if not audio_path:
            print("❌ 請輸入有效的檔案路徑")
            continue

        # 處理引號包圍的路徑
        if audio_path.startswith('"') and audio_path.endswith('"'):
            audio_path = audio_path[1:-1]

        if not validate_audio_file(audio_path):
            continue

        # 選擇模型
        models = get_available_models()
        print(f"\n🤖 選擇模型 (預設: base):")
        for i, model in enumerate(models):
            print(f"  {i+1}. {model}")

        model_choice = input(">>> ").strip()
        if model_choice.isdigit() and 1 <= int(model_choice) <= len(models):
            model_name = models[int(model_choice) - 1]
        elif model_choice in models:
            model_name = model_choice
        else:
            model_name = "base"

        # 選擇語言
        languages = get_supported_languages()
        print(f"\n🌐 選擇語言 (預設: en):")
        for code, name in languages.items():
            print(f"  {code}: {name}")

        lang_choice = input(">>> ").strip().lower()
        if lang_choice in languages:
            language = lang_choice
        else:
            language = "en"

        # 輸出路徑
        print(f"\n📝 輸出路徑 (預設: 與音訊檔案同目錄):")
        output_path = input(">>> ").strip()
        if output_path.startswith('"') and output_path.endswith('"'):
            output_path = output_path[1:-1]

        output_path = output_path if output_path else None

        # 開始轉錄
        print(f"\n🚀 開始轉錄...")
        success = transcribe_to_srt(audio_path, output_path, model_name, language)

        if success:
            print("\n✅ 轉錄完成！")
        else:
            print("\n❌ 轉錄失敗")

        print("\n" + "=" * 50)


def main():
    """主程式"""
    if len(sys.argv) == 1:
        # 沒有參數時啟動交談式模式
        interactive_mode()
    else:
        # 命令列模式
        if len(sys.argv) < 2:
            print("用法: python script.py <音訊檔案> [輸出路徑] [模型] [語言]")
            print("或直接執行進入交談式模式")
            return

        audio_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        model_name = sys.argv[3] if len(sys.argv) > 3 else "base"
        language = sys.argv[4] if len(sys.argv) > 4 else "en"

        success = transcribe_to_srt(audio_path, output_path, model_name, language)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
