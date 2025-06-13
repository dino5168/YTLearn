import pysrt
from googletrans import Translator
import time
import os


def translate_srt_google(input_file, output_file, target_language="zh-tw", delay=0.1):
    """
    使用 Google Translate 翻譯 SRT 字幕檔案

    參數:
    - input_file: 輸入的 SRT 檔案路徑
    - output_file: 輸出的 SRT 檔案路徑
    - target_language: 目標語言代碼 (預設: zh-tw 繁體中文)
    - delay: 每次翻譯間的延遲秒數 (避免被限制)
    """

    # 檢查輸入檔案是否存在
    if not os.path.exists(input_file):
        print(f"錯誤: 找不到檔案 {input_file}")
        return False

    try:
        # 讀取 SRT 檔案
        print(f"正在讀取檔案: {input_file}")
        subs = pysrt.open(input_file, encoding="utf-8")
        print(f"總共有 {len(subs)} 條字幕")

        # 初始化翻譯器
        translator = Translator()

        # 翻譯每條字幕
        successful_translations = 0
        failed_translations = 0

        for i, sub in enumerate(subs):
            try:
                # 跳過空白字幕
                if not sub.text.strip():
                    continue

                # 翻譯
                translated = translator.translate(sub.text, dest=target_language)
                sub.text = translated.text
                successful_translations += 1

                # 顯示進度
                progress = (i + 1) / len(subs) * 100
                print(
                    f"翻譯進度: {i+1}/{len(subs)} ({progress:.1f}%) - 成功: {successful_translations}, 失敗: {failed_translations}"
                )

                # 延遲避免被限制
                time.sleep(delay)

            except Exception as e:
                print(f"翻譯第 {i+1} 條字幕失敗: {e}")
                failed_translations += 1
                # 翻譯失敗時保留原文
                continue

        # 儲存翻譯後的檔案
        print(f"正在儲存到: {output_file}")
        subs.save(output_file, encoding="utf-8")

        print(f"\n翻譯完成!")
        print(f"成功翻譯: {successful_translations} 條")
        print(f"翻譯失敗: {failed_translations} 條")
        print(f"檔案已儲存至: {output_file}")

        return True

    except Exception as e:
        print(f"處理檔案時發生錯誤: {e}")
        return False


def batch_translate_srt(input_file, output_file, target_language="zh-tw", batch_size=5):
    """
    批次翻譯版本 - 一次翻譯多條字幕，減少 API 呼叫次數
    """

    if not os.path.exists(input_file):
        print(f"錯誤: 找不到檔案 {input_file}")
        return False

    try:
        subs = pysrt.open(input_file, encoding="utf-8")
        translator = Translator()

        print(f"總共有 {len(subs)} 條字幕，將以 {batch_size} 條為一批進行翻譯")

        for i in range(0, len(subs), batch_size):
            batch_end = min(i + batch_size, len(subs))
            batch = subs[i:batch_end]

            # 合併字幕文字
            texts_to_translate = []
            for sub in batch:
                if sub.text.strip():
                    texts_to_translate.append(sub.text)

            if texts_to_translate:
                # 用特殊分隔符號合併
                combined_text = " ||| ".join(texts_to_translate)

                try:
                    # 翻譯
                    translated = translator.translate(
                        combined_text, dest=target_language
                    )
                    translated_texts = translated.text.split(" ||| ")

                    # 分配翻譯結果
                    text_index = 0
                    for j, sub in enumerate(batch):
                        if sub.text.strip() and text_index < len(translated_texts):
                            subs[i + j].text = translated_texts[text_index].strip()
                            text_index += 1

                    print(f"批次 {i//batch_size + 1} 翻譯完成 ({i+1}-{batch_end})")

                except Exception as e:
                    print(f"批次 {i//batch_size + 1} 翻譯失敗: {e}")

            # 延遲
            time.sleep(0.5)

        subs.save(output_file, encoding="utf-8")
        print(f"批次翻譯完成! 檔案已儲存至: {output_file}")
        return True

    except Exception as e:
        print(f"批次翻譯時發生錯誤: {e}")
        return False


# 支援的語言代碼
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


def main():
    """
    主程式 - 使用範例
    """
    # 設定檔案路徑
    input_file = "c:/mp3/test/01.srt"  # 替換成你的輸入檔案
    output_file = "c:/mp3/test/01tw.srt"  # 輸出檔案名稱

    # 選擇翻譯語言
    target_lang = "zh-tw"  # 繁體中文

    print("開始翻譯 SRT 字幕檔案...")
    print(f"輸入檔案: {input_file}")
    print(f"輸出檔案: {output_file}")
    print(f"目標語言: {target_lang}")
    print("-" * 50)

    # 選擇翻譯方式
    use_batch = input("使用批次翻譯模式嗎? (y/n, 預設: n): ").lower().strip()
    input_file = input("輸入原始srt檔案")
    output_file = input("輸入輸出srt檔案")

    if use_batch == "y":
        # 批次翻譯 (較快，但可能準確度稍低)
        success = batch_translate_srt(input_file, output_file, target_lang)
    else:
        # 逐條翻譯 (較慢，但準確度較高)
        success = translate_srt_google(input_file, output_file, target_lang)

    if success:
        print("\n✅ 翻譯成功完成!")
    else:
        print("\n❌ 翻譯過程中發生錯誤")


if __name__ == "__main__":
    # 使用前請先安裝必要套件:
    # pip install pysrt googletrans==4.0.0-rc1

    main()
