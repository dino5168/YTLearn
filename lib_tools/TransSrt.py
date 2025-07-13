import pysrt
from googletrans import Translator
import os
import time


def translate_and_merge_srt(
    input_file, output_file, source_lang="en", target_lang="zh-tw", delay=0.5
):
    if not os.path.exists(input_file):
        print(f"錯誤: 找不到檔案 {input_file}")
        return False

    try:
        subs = pysrt.open(input_file, encoding="utf-8")
        translator = Translator()
        successful = 0
        failed = 0

        for i, sub in enumerate(subs):
            original_text = sub.text.strip()
            if not original_text:
                continue
            try:
                translated = translator.translate(
                    original_text, src=source_lang, dest=target_lang
                )
                # 合併英文與中文字幕，中間換行分隔
                sub.text = f"{original_text}\n{translated.text}"
                successful += 1
            except Exception as e:
                print(f"第 {i+1} 條字幕翻譯失敗: {e}")
                failed += 1
            time.sleep(delay)

        subs.save(output_file, encoding="utf-8")
        print(f"✅ 翻譯並合併完成! 成功: {successful}, 失敗: {failed}")
        print(f"輸出檔案: {output_file}")
        return True

    except Exception as e:
        print(f"處理檔案時發生錯誤: {e}")
        return False


def main():
    print("🌍 英文 SRT 翻譯合併器 (英文 + 中文)")
    print("-" * 40)
    input_file = input("請輸入英文 SRT 檔案路徑: ").strip()
    output_file = input("請輸入輸出合併後 SRT 檔案路徑: ").strip()

    translate_and_merge_srt(input_file, output_file)


if __name__ == "__main__":
    # 需要安裝 pysrt 與 googletrans
    # pip install pysrt googletrans==4.0.0-rc1
    main()
