from PIL import Image

print("👋 嗨～我可以幫你把圖片背景變成透明喔！")

# ✅ 輸入原始圖片路徑，直到使用者輸入有效路徑
while True:
    input_path = input("請輸入原始圖片的路徑（例如：c:/temp/A02.png）：").strip()
    if input_path == "":
        print("❗ 請輸入檔案路徑，不能空白喔。")
        continue
    try:
        print(f"正在打開圖片：{input_path}")
        img = Image.open(input_path).convert("RGBA")
        print("✅ 圖片載入成功！")
        break
    except Exception as e:
        print("❌ 無法打開圖片，請確認路徑或檔名是否正確。")
        print(f"錯誤訊息：{e}")

# 處理圖片像素
datas = img.getdata()
new_data = []

print("🎨 正在處理圖片像素，把白色背景變透明...")

for index, item in enumerate(datas):
    r, g, b, a = item
    if r > 240 and g > 240 and b > 240:
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)
    if index % 50000 == 0:
        print(f"已處理 {index} 個像素...")

print("✅ 像素處理完成！")
img.putdata(new_data)

# ✅ 要儲存的輸出路徑，不得為空
while True:
    output_path = input("請輸入要儲存的檔案路徑（例如：c:/temp/output.png）：").strip()
    if output_path == "":
        print("❗ 儲存路徑不能是空的喔，請再輸入一次。")
        continue
    try:
        img.save(output_path, "PNG")
        print(f"✅ 圖片儲存成功！檔案位置：{output_path}")
        print("🎉 背景透明化任務完成！")
        break
    except Exception as e:
        print("❌ 儲存圖片時發生錯誤，請確認資料夾是否存在。")
        print(f"錯誤訊息：{e}")
