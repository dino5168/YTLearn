from bs4 import BeautifulSoup
import re
import os


def extract_title_and_content(html_file_path):
    """
    從HTML文件中提取標題和內容
    """
    try:
        # 讀取HTML文件
        with open(html_file_path, "r", encoding="big5") as file:
            html_content = file.read()

        # 解析HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # 提取標題 - 專門找 <font face="標楷體" size="6"> 標籤
        title = None

        # 尋找特定的字體標籤：face="標楷體" 且 size="6"
        title_font = soup.find("font", {"face": "標楷體", "size": "6"})
        if title_font:
            title = title_font.get_text().strip()

        # 如果沒找到，嘗試只用 size="6" 來找
        if not title:
            large_font = soup.find("font", {"size": "6"})
            if large_font:
                title = large_font.get_text().strip()

        # 如果還是沒找到標題，使用預設值
        if not title:
            title = "未命名文件"

        # 提取所有文本內容
        # 移除script和style標籤
        for script in soup(["script", "style"]):
            script.decompose()

        # 獲取純文本內容
        text_content = soup.get_text()

        # 清理文本內容
        # 移除多餘的空白和換行
        lines = text_content.split("\n")
        cleaned_lines = []
        for line in lines:  # 從第二行開始處理
            # print(f"處理行: {line}")  # 調試輸出
            line = line.strip()
            if line:  # 只保留非空行
                cleaned_lines.append(line)

        content = "\n".join(cleaned_lines[1:])  # 從第二行開始，因為第一行是標題])

        return title, content

    except Exception as e:
        print(f"讀取HTML文件時發生錯誤: {e}")
        return None, None


def sanitize_filename(filename):
    """
    清理檔案名稱，移除不合法的字元
    """
    # 移除或替換不合法的檔案名稱字元
    illegal_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for char in illegal_chars:
        filename = filename.replace(char, "_")

    # 限制檔案名稱長度
    if len(filename) > 100:
        filename = filename[:100]

    return filename


def save_content_to_file(title, content, output_dir="."):
    """
    將內容保存到以標題命名的文件中
    """
    try:
        # 清理檔案名稱
        safe_title = sanitize_filename(title)

        # 建立輸出檔案路徑
        output_file = os.path.join(output_dir, f"{safe_title}.txt")

        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)

        # 寫入文件
        with open(output_file, "w", encoding="utf-8") as file:
            # file.write(f"標題: {title}\n")
            # file.write("=" * 50 + "\n\n")
            file.write(content)

        print(f"內容已成功保存到: {output_file}")
        return output_file

    except Exception as e:
        print(f"保存文件時發生錯誤: {e}")
        return None


def main():
    """
    主程式
    """
    # HTML文件路徑
    html_file = r"C:\temp\a\output_1.html"  # 請根據實際路徑修改

    # 檢查文件是否存在
    if not os.path.exists(html_file):
        print(f"錯誤: 找不到文件 {html_file}")
        return

    # 提取標題和內容
    title, content = extract_title_and_content(html_file)

    if title and content:
        # print(f"提取的標題: {title}")
        # print(f"內容長度: {len(content)} 字元")

        # 保存到文件
        output_file = save_content_to_file(title, content)

        if output_file:
            print(f"\n處理完成！文件已保存為: {output_file}")
    else:
        print("無法提取標題和內容")


if __name__ == "__main__":
    main()
