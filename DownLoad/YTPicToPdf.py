import os
from PIL import Image


def images_to_pdf(img_dir, output_pdf_path="output.pdf"):
    # 支援的圖片副檔名
    extensions = (".jpg", ".jpeg", ".png")

    # 讀取所有圖片檔案並排序
    img_files = sorted(
        [f for f in os.listdir(img_dir) if f.lower().endswith(extensions)]
    )

    if not img_files:
        print("⚠️ 沒有找到圖片。")
        return

    # 開啟所有圖片並轉為 RGB（PDF 不支援透明）
    images = []
    for fname in img_files:
        path = os.path.join(img_dir, fname)
        img = Image.open(path).convert("RGB")
        images.append(img)

    # 儲存為 PDF（第一張是主圖，其他為附加頁）
    first_img = images[0]
    rest_imgs = images[1:]
    first_img.save(output_pdf_path, save_all=True, append_images=rest_imgs)
    print(f"🎉 PDF 已儲存為：{output_pdf_path}")


if __name__ == "__main__":
    img_dir = input("📁 請輸入圖片資料夾：").strip('" ')
    output_pdf_path = input("📄 請輸入輸出的 PDF 檔名（例如 output.pdf）：").strip('" ')
    if not output_pdf_path:
        output_pdf_path = "output.pdf"
    images_to_pdf(img_dir, output_pdf_path)
