import whisper
from pathlib import Path
import sys
import os
import subprocess
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


def check_ffmpeg() -> bool:
    """檢查 FFmpeg 是否可用"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def embed_subtitles(
    video_path: str, srt_path: str, output_path: Optional[str] = None
) -> bool:
    """
    使用 FFmpeg 將字幕嵌入到影片中

    參數:
        video_path: 原始影片路徑
        srt_path: SRT 字幕檔路徑
        output_path: 輸出影片路徑（可選）

    回傳:
        成功為 True，失敗為 False
    """
    if not check_ffmpeg():
        print("❌ 找不到 FFmpeg，請先安裝 FFmpeg")
        print("   下載網址：https://ffmpeg.org/download.html")
        return False

    video_path = Path(video_path)
    srt_path = Path(srt_path)

    if not video_path.exists():
        print(f"❌ 影片檔案不存在：{video_path}")
        return False

    if not srt_path.exists():
        print(f"❌ 字幕檔案不存在：{srt_path}")
        return False

    if output_path is None:
        output_path = str(video_path.with_suffix("").with_suffix(".with_subtitles.mp4"))

    print(f"🎬 原始影片：{video_path}")
    print(f"📝 字幕檔案：{srt_path}")
    print(f"📹 輸出影片：{output_path}")
    print("-" * 50)

    try:
        # 構建 FFmpeg 命令
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),  # 輸入影片
            "-i",
            str(srt_path),  # 輸入字幕
            "-c:v",
            "copy",  # 複製影片流（不重新編碼）
            "-c:a",
            "copy",  # 複製音訊流（不重新編碼）
            "-c:s",
            "mov_text",  # 字幕編碼格式
            "-metadata:s:s:0",
            "language=eng",  # 設定字幕語言
            "-disposition:s:0",
            "default",  # 設定為預設字幕
            "-y",  # 覆寫輸出檔案
            str(output_path),
        ]

        print("🔄 開始嵌入字幕...")
        print("   這可能需要一些時間，請耐心等待...")

        # 執行 FFmpeg 命令
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300  # 5分鐘超時
        )

        if result.returncode == 0:
            print("✅ 字幕嵌入成功！")
            print(f"   📹 輸出檔案：{output_path}")

            # 檢查檔案大小
            original_size = video_path.stat().st_size
            output_size = Path(output_path).stat().st_size
            print(f"   📊 原始檔案：{original_size / (1024*1024):.1f} MB")
            print(f"   📊 輸出檔案：{output_size / (1024*1024):.1f} MB")

            return True
        else:
            print("❌ 字幕嵌入失敗")
            print("FFmpeg 錯誤訊息：")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ 處理超時（超過5分鐘）")
        return False
    except Exception as e:
        print(f"❌ 嵌入字幕時發生錯誤：{e}")
        return False


def burn_subtitles(
    video_path: str, srt_path: str, output_path: Optional[str] = None
) -> bool:
    """
    使用 FFmpeg 將字幕燒錄到影片中（硬字幕）

    參數:
        video_path: 原始影片路徑
        srt_path: SRT 字幕檔路徑
        output_path: 輸出影片路徑（可選）

    回傳:
        成功為 True，失敗為 False
    """
    if not check_ffmpeg():
        print("❌ 找不到 FFmpeg，請先安裝 FFmpeg")
        return False

    video_path = Path(video_path)
    srt_path = Path(srt_path)

    if not video_path.exists():
        print(f"❌ 影片檔案不存在：{video_path}")
        return False

    if not srt_path.exists():
        print(f"❌ 字幕檔案不存在：{srt_path}")
        return False

    if output_path is None:
        output_path = str(
            video_path.with_suffix("").with_suffix(".burned_subtitles.mp4")
        )

    print(f"🎬 原始影片：{video_path}")
    print(f"📝 字幕檔案：{srt_path}")
    print(f"📹 輸出影片：{output_path}")
    print("-" * 50)

    try:
        # 構建 FFmpeg 命令（燒錄字幕）
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            f"subtitles={str(srt_path)}",  # 使用 subtitles 濾鏡
            "-c:a",
            "copy",  # 複製音訊流
            "-y",  # 覆寫輸出檔案
            str(output_path),
        ]

        print("🔄 開始燒錄字幕...")
        print("   ⚠️  注意：燒錄字幕需要重新編碼，時間較長")

        # 執行 FFmpeg 命令
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600  # 10分鐘超時
        )

        if result.returncode == 0:
            print("✅ 字幕燒錄成功！")
            print(f"   📹 輸出檔案：{output_path}")
            return True
        else:
            print("❌ 字幕燒錄失敗")
            print("FFmpeg 錯誤訊息：")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ 處理超時（超過10分鐘）")
        return False
    except Exception as e:
        print(f"❌ 燒錄字幕時發生錯誤：{e}")
        return False


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

            # 檢查是否為影片檔案，提供字幕嵌入選項
            audio_file = Path(audio_path)
            video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}

            if audio_file.suffix.lower() in video_extensions:
                srt_path = (
                    output_path if output_path else str(audio_file.with_suffix(".srt"))
                )

                print(f"\n🎬 偵測到影片檔案！是否要將字幕加入影片？")
                print("  1. 嵌入字幕（軟字幕，可開關）")
                print("  2. 燒錄字幕（硬字幕，永久顯示）")
                print("  3. 跳過")

                subtitle_choice = input(">>> ").strip()

                if subtitle_choice == "1":
                    print("\n🔄 嵌入字幕到影片...")
                    embed_success = embed_subtitles(audio_path, srt_path)
                    if embed_success:
                        print("✅ 字幕嵌入完成！")
                    else:
                        print("❌ 字幕嵌入失敗")

                elif subtitle_choice == "2":
                    print("\n🔄 燒錄字幕到影片...")
                    burn_success = burn_subtitles(audio_path, srt_path)
                    if burn_success:
                        print("✅ 字幕燒錄完成！")
                    else:
                        print("❌ 字幕燒錄失敗")
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
        if sys.argv[1] in ["--help", "-h"]:
            print("🎤 Whisper 音訊轉錄工具")
            print("=" * 50)
            print("使用方法:")
            print("  python transcriber.py                          # 交談式模式")
            print("  python transcriber.py <音訊檔案>               # 基本轉錄")
            print("  python transcriber.py <音訊檔案> [選項]        # 完整參數")
            print("\n參數:")
            print("  音訊檔案    必要參數，音訊或影片檔案路徑")
            print("  輸出路徑    可選，SRT 字幕檔輸出路徑")
            print("  模型       可選，Whisper 模型 (tiny/base/small/medium/large)")
            print("  語言       可選，語言代碼 (en/zh/ja/ko/auto 等)")
            print("\n字幕嵌入:")
            print("  --embed     嵌入軟字幕到影片")
            print("  --burn      燒錄硬字幕到影片")
            print("\n範例:")
            print("  python transcriber.py video.mp4")
            print("  python transcriber.py video.mp4 subtitle.srt medium en")
            print("  python transcriber.py video.mp4 --embed")
            print("  python transcriber.py video.mp4 --burn")
            return

        if len(sys.argv) < 2:
            print("❌ 請提供音訊檔案路徑")
            print("使用 --help 查看詳細說明")
            return

        audio_path = sys.argv[1]

        # 檢查是否為字幕嵌入模式
        if "--embed" in sys.argv or "--burn" in sys.argv:
            # 假設 SRT 檔案與影片同名
            srt_path = str(Path(audio_path).with_suffix(".srt"))

            if not Path(srt_path).exists():
                print(f"❌ 找不到字幕檔案：{srt_path}")
                print("請先轉錄生成字幕檔案")
                return

            if "--embed" in sys.argv:
                success = embed_subtitles(audio_path, srt_path)
            else:  # --burn
                success = burn_subtitles(audio_path, srt_path)

            sys.exit(0 if success else 1)

        # 一般轉錄模式
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        model_name = sys.argv[3] if len(sys.argv) > 3 else "base"
        language = sys.argv[4] if len(sys.argv) > 4 else "en"

        success = transcribe_to_srt(audio_path, output_path, model_name, language)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
