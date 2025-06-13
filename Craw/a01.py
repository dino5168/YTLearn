import os
from outputtxt import extract_title_and_content
from outputtxt import save_content_to_file

folder_path = r"C:\temp\佛教故事\html"  # 修改成你的資料夾路徑
output_path = r"C:\temp\佛教故事\txt"  # 修改成你的輸出路徑

files = os.listdir(folder_path)

for file_name in files:
    html_file = os.path.join(folder_path, file_name)
    print(html_file)
    # 檢查文件是否存在
    if not os.path.exists(html_file):
        print(f"錯誤: 找不到文件 {html_file}")
        continue

    # 提取標題和內容
    title, content = extract_title_and_content(html_file)

    if title and content:
        # print(f"提取的標題: {title}")
        # print(f"內容長度: {len(content)} 字元")

        # 保存到文件
        output_file = save_content_to_file(title, content, output_path)

        if output_file:
            print(f"\n處理完成！文件已保存為: {output_file}")
    else:
        print("無法提取標題和內容")
