import os
from PIL import Image, ImageDraw, ImageFont
import pysrt
import re


def split_chinese_english(text):
    chinese = "".join(re.findall(r"[\u4e00-\u9fff，。！？；：「」、《》（）]", text))
    english = "".join(re.findall(r"[^\u4e00-\u9fff，。！？；：「」、《》（）]+", text))
    return chinese.strip(), english.strip()


def draw_subtitles_on_images(
    img_dir, srt_path, output_dir="output_images_with_subtitles"
):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    subs = pysrt.open(srt_path, encoding="utf-8")
    print(f"✅ 讀取字幕：{len(subs)} 行")

    img_files = sorted(
        [
            f
            for f in os.listdir(img_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
    )
    print(f"✅ 找到圖片：{len(img_files)} 張")

    if len(img_files) != len(subs):
        print("⚠️ 圖片數量與字幕數不一致，請確認！")
        return
    # C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenSenRounded-R.ttf
    font_path = r"C:\Users\DINO\AppData\Local\Microsoft\Windows\Fonts\BpmfGenSenRounded-R.ttf"  # 微軟正黑體
    font_size = 28
    font = ImageFont.truetype(font_path, font_size)

    for idx, (img_file, sub) in enumerate(zip(img_files, subs), start=1):
        img_path = os.path.join(img_dir, img_file)
        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # 處理字幕內容
        text = sub.text.strip().replace("\n", " ")
        zh, en = split_chinese_english(text)
        lines = [en, zh] if zh and en else [text]

        # 計算文字大小
        line_sizes = []
        total_height = 0
        max_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_sizes.append((line, w, h))
            total_height += h
            max_width = max(max_width, w)
        total_height += (len(lines) - 1) * 10  # 行間距

        # 框框座標與設定
        padding = 16
        x = (img.width - max_width) / 2 - padding
        y = img.height - total_height - 40 - padding
        box_w = max_width + 2 * padding
        box_h = total_height + 2 * padding

        # 畫圓角背景框
        draw.rounded_rectangle(
            [x, y, x + box_w, y + box_h],
            radius=20,
            fill="#002244",
        )

        # 畫每一行文字（置中）
        text_y = y + padding
        for line, w, h in line_sizes:
            text_x = (img.width - w) / 2
            draw.text((text_x, text_y), line, font=font, fill="white")
            text_y += h + 10

        # 儲存圖片
        output_path = os.path.join(output_dir, img_file)
        img.save(output_path)
        print(f"✅ 已儲存：{output_path}")

    print(f"\n🎉 所有圖片字幕處理完成，共 {len(img_files)} 張")


if __name__ == "__main__":
    img_dir = input("📁 請輸入圖片資料夾（如 img）：").strip('" ')
    srt_path = input("📄 請輸入 SRT 字幕檔路徑：").strip('" ')
    output_dir = input(
        "📤 請輸入輸出資料夾（預設 output_images_with_subtitles）："
    ).strip('" ')
    if not output_dir:
        output_dir = "output_images_with_subtitles"

    draw_subtitles_on_images(img_dir, srt_path, output_dir)
