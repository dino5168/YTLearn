import os
import srt
from pydub import AudioSegment
from datetime import timedelta


def get_file_path(file_type, extension):
    """取得檔案路徑的輔助函數"""
    while True:
        file_path = (
            input(f"請輸入 {file_type} 檔案的路徑 (或拖拉檔案到這裡): ")
            .strip()
            .strip('"')
        )

        if not file_path:
            print("檔案路徑不能為空，請重新輸入。")
            continue

        if not os.path.exists(file_path):
            print(f"找不到檔案: {file_path}")
            print("請確認檔案路徑是否正確。")
            continue

        if not file_path.lower().endswith(extension):
            print(f"檔案格式不正確，需要 {extension} 檔案。")
            continue

        return file_path


def get_output_directory():
    """取得輸出目錄"""
    default_dir = "split_audio"
    output_dir = input(f"請輸入輸出資料夾名稱 (預設: {default_dir}): ").strip()

    if not output_dir:
        output_dir = default_dir

    return output_dir


def confirm_settings(mp3_file, srt_file, output_dir):
    """確認設定"""
    print("\n" + "=" * 50)
    print("請確認以下設定:")
    print(f"MP3 檔案: {mp3_file}")
    print(f"SRT 檔案: {srt_file}")
    print(f"輸出資料夾: {output_dir}")
    print("=" * 50)

    while True:
        confirm = input("確認開始切割嗎? (y/n): ").strip().lower()
        if confirm in ["y", "yes", "是"]:
            return True
        elif confirm in ["n", "no", "否"]:
            return False
        else:
            print("請輸入 y 或 n")


def preview_subtitles(srt_file):
    """預覽字幕內容"""
    try:
        with open(srt_file, "r", encoding="utf-8") as f:
            srt_content = f.read()

        subtitles = list(srt.parse(srt_content))
        print(f"\n找到 {len(subtitles)} 個字幕片段")

        while True:
            preview = input("要預覽前幾個字幕片段嗎? (y/n): ").strip().lower()
            if preview in ["y", "yes", "是"]:
                preview_count = min(5, len(subtitles))
                print(f"\n前 {preview_count} 個字幕片段:")
                print("-" * 40)
                for i, subtitle in enumerate(subtitles[:preview_count]):
                    print(f"{i+1:03d}. {subtitle.start} - {subtitle.end}")
                    print(f"     {subtitle.content.strip()}")
                    print()
                break
            elif preview in ["n", "no", "否"]:
                break
            else:
                print("請輸入 y 或 n")

        return subtitles
    except Exception as e:
        print(f"讀取 SRT 檔案時發生錯誤: {e}")
        return None


def timedelta_to_ms(td):
    """將 timedelta 物件轉換為毫秒"""
    return int(td.total_seconds() * 1000)


def split_mp3_by_srt(mp3_file_path, srt_file_path, output_dir):
    """根據 SRT 字幕檔案的時間序列切割 MP3 檔案"""

    # 建立輸出資料夾
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已建立輸出資料夾: {output_dir}")

    # 讀取 MP3 檔案
    print(f"\n正在載入 MP3 檔案...")
    try:
        audio = AudioSegment.from_mp3(mp3_file_path)
        print(f"MP3 檔案載入成功 (長度: {len(audio)/1000:.2f} 秒)")
    except Exception as e:
        print(f"載入 MP3 檔案時發生錯誤: {e}")
        return False

    # 讀取並解析 SRT 檔案
    try:
        with open(srt_file_path, "r", encoding="utf-8") as f:
            srt_content = f.read()
        subtitles = list(srt.parse(srt_content))
    except Exception as e:
        print(f"讀取 SRT 檔案時發生錯誤: {e}")
        return False

    print(f"\n開始切割音訊...")
    success_count = 0

    # 逐一切割音訊
    for i, subtitle in enumerate(subtitles):
        try:
            # 將時間轉換為毫秒
            start_ms = timedelta_to_ms(subtitle.start)
            end_ms = timedelta_to_ms(subtitle.end)

            # 切割音訊片段
            audio_segment = audio[start_ms:end_ms]

            # 輸出檔案名稱
            output_filename = f"{i+1:03d}.mp3"
            output_path = os.path.join(output_dir, output_filename)

            # 匯出音訊片段
            audio_segment.export(output_path, format="mp3")

            success_count += 1
            print(
                f"✓ {output_filename} ({subtitle.start} - {subtitle.end}) - {len(audio_segment)/1000:.2f}秒"
            )

        except Exception as e:
            print(f"✗ 處理第 {i+1} 個片段時發生錯誤: {e}")

    print(f"\n切割完成！成功處理 {success_count}/{len(subtitles)} 個片段")
    print(f"檔案已儲存到: {os.path.abspath(output_dir)}")
    return True


def main():
    """主程式"""
    print("=" * 60)
    print("     MP3 音訊檔依據 SRT 字幕切割工具")
    print("=" * 60)

    while True:
        try:
            # 取得檔案路徑
            print("\n1. 選擇檔案")
            mp3_file = get_file_path("MP3 音訊", ".mp3")
            srt_file = get_file_path("SRT 字幕", ".srt")

            # 預覽字幕
            print("\n2. 預覽字幕")
            subtitles = preview_subtitles(srt_file)
            if subtitles is None:
                continue

            # 設定輸出目錄
            print("\n3. 設定輸出")
            output_dir = get_output_directory()

            # 確認設定
            print("\n4. 確認設定")
            if not confirm_settings(mp3_file, srt_file, output_dir):
                print("已取消操作。")
                continue

            # 執行切割
            print("\n5. 執行切割")
            success = split_mp3_by_srt(mp3_file, srt_file, output_dir)

            if success:
                print("\n🎉 切割完成！")
            else:
                print("\n❌ 切割過程中發生錯誤。")

        except KeyboardInterrupt:
            print("\n\n程式已中斷。")
            break
        except Exception as e:
            print(f"\n發生未預期的錯誤: {e}")

        # 詢問是否繼續
        print("\n" + "-" * 40)
        while True:
            continue_choice = input("要處理其他檔案嗎? (y/n): ").strip().lower()
            if continue_choice in ["y", "yes", "是"]:
                break
            elif continue_choice in ["n", "no", "否"]:
                print("感謝使用！再見～")
                return
            else:
                print("請輸入 y 或 n")


if __name__ == "__main__":
    main()
