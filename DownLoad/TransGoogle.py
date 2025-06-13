import pysrt
from googletrans import Translator
import time
import os

LANGUAGE_CODES = {
    "繁體中文": "zh-tw",
    "簡體中文": "zh-cn",
    "英文": "en",
    "日文": "ja",
    "韓文": "ko",
    "法文": "fr",
    "德文": "de",
    "西班牙文": "es",
    "義大利文": "it",
    "俄文": "ru",
    "泰文": "th",
    "越南文": "vi",
}


def translate_srt_google(
    input_file, output_file, source_language, target_language, delay=0.5
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
            if not sub.text.strip():
                continue
            try:
                translated = translator.translate(
                    sub.text, src=source_language, dest=target_language
                )
                sub.text = translated.text
                successful += 1
            except Exception as e:
                print(f"第 {i+1} 條字幕翻譯失敗: {e}")
                failed += 1
            time.sleep(delay)

        subs.save(output_file, encoding="utf-8")
        print(f"✅ 翻譯完成! 成功: {successful}, 失敗: {failed}")
        return True

    except Exception as e:
        print(f"處理檔案時發生錯誤: {e}")
        return False


def batch_translate_srt(
    input_file, output_file, source_language, target_language, batch_size=5
):
    if not os.path.exists(input_file):
        print(f"錯誤: 找不到檔案 {input_file}")
        return False

    try:
        subs = pysrt.open(input_file, encoding="utf-8")
        translator = Translator()

        for i in range(0, len(subs), batch_size):
            batch = subs[i : i + batch_size]
            texts = [sub.text.strip() for sub in batch if sub.text.strip()]
            combined = " ||| ".join(texts)

            if not combined:
                continue

            try:
                translated = translator.translate(
                    combined, src=source_language, dest=target_language
                )
                parts = translated.text.split(" ||| ")
                j = 0
                for idx, sub in enumerate(batch):
                    if sub.text.strip() and j < len(parts):
                        subs[i + idx].text = parts[j].strip()
                        j += 1
                print(f"批次翻譯完成: {i+1} - {i+len(batch)}")
            except Exception as e:
                print(f"批次翻譯失敗: {e}")
            time.sleep(0.5)

        subs.save(output_file, encoding="utf-8")
        print(f"✅ 批次翻譯完成並儲存至: {output_file}")
        return True

    except Exception as e:
        print(f"處理檔案時發生錯誤: {e}")
        return False


def choose_language(prompt_text):
    print(prompt_text)
    for i, (lang_name, code) in enumerate(LANGUAGE_CODES.items()):
        print(f"{i+1}. {lang_name} ({code})")
    while True:
        try:
            choice = int(input("請選擇語言編號: "))
            if 1 <= choice <= len(LANGUAGE_CODES):
                return list(LANGUAGE_CODES.values())[choice - 1]
        except ValueError:
            pass
        print("無效選擇，請重新輸入。")


def main():
    print("🌍 SRT 字幕翻譯器（Google Translate）")
    print("-" * 40)

    # 選擇原始語言與目標語言
    source_lang = choose_language("請選擇來源語言:")
    target_lang = choose_language("請選擇目標語言:")

    # 輸入檔案與輸出檔案
    input_file = input("請輸入來源 SRT 檔案路徑: ").strip()
    output_file = input("請輸入輸出 SRT 檔案路徑: ").strip()

    # 選擇翻譯模式
    use_batch = input("是否使用批次翻譯? (y/n): ").lower().strip() == "y"

    if use_batch:
        batch_translate_srt(input_file, output_file, source_lang, target_lang)
    else:
        translate_srt_google(input_file, output_file, source_lang, target_lang)


if __name__ == "__main__":
    # 執行前請確認安裝:
    # pip install pysrt googletrans==4.0.0-rc1
    main()
