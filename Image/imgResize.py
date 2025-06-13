from PIL import Image

# 開啟原始圖片
img = Image.open(r"C:\英語\封面.png")

# 調整大小到 1792 x 1024（不保留比例）
resized_img = img.resize((1792, 1024), Image.Resampling.LANCZOS)

# 儲存成新圖片
resized_img.save(r"C:\英語\封面01.png")
