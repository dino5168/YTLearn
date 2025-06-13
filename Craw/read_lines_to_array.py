def read_lines_to_array(filepath: str, encoding: str = "utf-8") -> list:
    """
    讀取文字檔每一行，並存到 list 中（自動去除換行符號）

    :param filepath: 檔案路徑
    :param encoding: 編碼格式（預設為 utf-8）
    :return: 每一行文字組成的 list
    """
    lines = []
    try:
        with open(filepath, "r", encoding=encoding) as file:
            for line in file:
                lines.append(line.strip())  # 去掉換行符號
    except Exception as e:
        print(f"讀取錯誤：{e}")
    return lines
