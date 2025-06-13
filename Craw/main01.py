# 輸出檔案
from read_lines_to_array import read_lines_to_array
from download import download_html

if __name__ == "__main__":
    filepath = "minlun_links_simple.txt"
    result = read_lines_to_array(filepath)
    for i, line in enumerate(result, 1):
        download_html(line.strip(), f"c:/temp/佛教故事/html/output_{i}.html")
        print(f"{i:2d}. {line}")
