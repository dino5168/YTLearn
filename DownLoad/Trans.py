import pysrt
from translate import Translator
import time
import os

LANGUAGE_CODES = {
    "繁體中文": "zh-TW",
    "簡體中文": "zh-CN",
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


def translate_srt_basic(
    input_file, output_file, source_language, target_language, delay=0.5
):
    if not os.path.exists(input_file):
        print(f"錯誤: 找不到檔案 {input_file}")
        return False

    try:
        subs = pysrt.open(input_file, encoding="utf-8")
        translator = Translator(from_lang=source_language, to_lang=target_language)

        successful = 0
        failed = 0

        for i, sub in enumerate(subs):
            if not sub.text.strip():
                continue
            try:
                translated_text = translator.translate(sub.text)
                sub.text = translated_text
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
    print("🌍 SRT 字幕翻譯器（使用 translate 套件）")
    print("-" * 40)

    source_lang = choose_language("請選擇來源語言:")
    target_lang = choose_language("請選擇目標語言:")

    input_file = input("請輸入來源 SRT 檔案路徑: ").strip()
    output_file = input("請輸入輸出 SRT 檔案路徑: ").strip()

    translate_srt_basic(input_file, output_file, source_lang, target_lang)


if __name__ == "__main__":
    # 執行前請確認安裝:
    # pip install pysrt translate
    main()
