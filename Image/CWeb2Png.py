import os
from PIL import Image

input_folder = r"C:\youtube\EglishKidstory"
output_folder = "C:\youtube\EglishKidstory"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".webp"):
        webp_path = os.path.join(input_folder, filename)
        png_path = os.path.join(output_folder, filename.replace(".webp", ".png"))

        with Image.open(webp_path) as img:
            img.save(png_path, "PNG")
            print(f"已轉換：{filename} → {os.path.basename(png_path)}")

print("全部轉換完成！")
