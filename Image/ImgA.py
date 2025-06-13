from PIL import Image

# 設定尺寸
width, height = 1792, 1024

# 建立一張 RGBA 空白圖片（預設為透明）
img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

# 填滿左半邊為深藍色（RGB: 0, 0, 139，Alpha: 255）
for x in range(width // 2):  # 左半邊
    for y in range(height):
        img.putpixel((x, y), (0, 0, 139, 255))  # 深藍不透明

# 右半邊維持預設透明

# 儲存圖片
img.save("c:/temp/half_blue_half_transparent.png", "PNG")
