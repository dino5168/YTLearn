import asyncio
import json
from pathlib import Path

# 載入你之前定義的 StoryVoiceGenerator 類別，假設在同目錄story_voice_generator.py
from StoryVoiceGenerator import StoryVoiceGenerator
import pysrt
from googletrans import Translator
import os
import time


async def translate_and_merge_srt(
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


async def generate_from_json(
    json_file: str, output_dir: str = "c:/temp/0717/story_outputs"
):
    # 讀 JSON 檔案
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 逐筆產生語音和字幕
    for item in data:
        voice = item.get("selectedValue", "en-US-JennyNeural")
        text = item.get("text", "")
        id_ = item.get("id", 0)

        # 指定輸出檔名(含id避免覆蓋)
        output_mp3 = f"note_{id_}.mp3"
        output_srt = f"note_{id_}.srt"

        generator = StoryVoiceGenerator(
            voice=voice,
            output_dir=output_dir,
            output_mp3=output_mp3,
            output_srt=output_srt,
        )
        print(f"\n➡️ 產生 id={id_} 使用語音 {voice}")
        await generator.generate_story_from_text(text)

        input_srt = os.path.join(output_dir, output_srt)
        output_srt_zhtw = os.path.join(output_dir, f"note_{id_}.zhtw.srt")
        await translate_and_merge_srt(input_srt, output_srt_zhtw)


if __name__ == "__main__":
    # 你 JSON 檔路徑，請改成你的實際路徑
    json_path = "c:/temp/0717/data/voice_data_20250717_081639.json"
    asyncio.run(generate_from_json(json_path))
