import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urlparse, urljoin
from pathlib import Path


def sanitize_filename(filename):
    """
    清理檔名，移除不合法的字元

    Args:
        filename (str): 原始檔名

    Returns:
        str: 清理後的檔名
    """
    # 移除或替換不合法的字元
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    filename = filename.replace(" ", "_")
    # 限制檔名長度
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def get_page_title(soup):
    """
    從HTML中提取頁面標題

    Args:
        soup: BeautifulSoup物件

    Returns:
        str: 頁面標題
    """
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    return "untitled"


def download_html_from_links(input_file, output_dir="downloaded_html", delay=1):
    """
    從文字檔讀取連結並下載HTML檔案

    Args:
        input_file (str): 包含連結的文字檔路徑
        output_dir (str): 輸出目錄
        delay (int): 每次請求間的延遲時間（秒）
    """

    # 建立輸出目錄
    Path(output_dir).mkdir(exist_ok=True)

    # 設定請求標頭
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 讀取連結檔案
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"找不到檔案: {input_file}")
        return
    except Exception as e:
        print(f"讀取檔案錯誤: {e}")
        return

    print(f"找到 {len(links)} 個連結")

    # 成功和失敗計數
    success_count = 0
    failed_count = 0
    failed_links = []

    # 處理每個連結
    for i, url in enumerate(links, 1):
        print(f"\n處理第 {i}/{len(links)} 個連結: {url}")

        try:
            # 發送請求
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # 專門針對繁體中文網站的編碼處理
            html_content = None
            used_encoding = None

            # 1. 首先檢查HTTP響應頭中的編碼
            content_type = response.headers.get("content-type", "").lower()
            if "charset=" in content_type:
                declared_encoding = content_type.split("charset=")[-1].strip()
                print(f"    HTTP頭聲明編碼: {declared_encoding}")

            # 2. 檢查HTML中的meta標籤編碼聲明
            raw_content = response.content
            meta_encoding = None
            try:
                # 用bytes搜尋meta標籤
                raw_text = raw_content.decode("ascii", errors="ignore").lower()
                if "charset=" in raw_text:
                    import re

                    charset_match = re.search(r'charset=["\']?([^"\'>\s]+)', raw_text)
                    if charset_match:
                        meta_encoding = charset_match.group(1)
                        print(f"    Meta標籤聲明編碼: {meta_encoding}")
            except:
                pass

            # 3. 嘗試不同編碼，優先使用Big5（繁體中文常用）
            encodings_to_try = []

            # 加入聲明的編碼
            if meta_encoding:
                encodings_to_try.append(meta_encoding)
            if "charset=" in content_type:
                declared_encoding = content_type.split("charset=")[-1].strip()
                if declared_encoding not in encodings_to_try:
                    encodings_to_try.append(declared_encoding)

            # 加入常見的繁體中文編碼
            common_encodings = ["big5", "utf-8", "big5-hkscs", "cp950", "gb2312", "gbk"]
            for enc in common_encodings:
                if enc not in encodings_to_try:
                    encodings_to_try.append(enc)

            # 嘗試每種編碼
            for encoding in encodings_to_try:
                try:
                    decoded_text = raw_content.decode(encoding)

                    # 檢查解碼後的內容品質
                    soup = BeautifulSoup(decoded_text, "html.parser")
                    text_content = soup.get_text()

                    # 檢查是否包含常見的繁體中文字符
                    traditional_chars = [
                        "的",
                        "一",
                        "是",
                        "在",
                        "有",
                        "不",
                        "和",
                        "人",
                        "這",
                        "中",
                        "大",
                        "為",
                        "上",
                        "個",
                        "國",
                        "我",
                        "以",
                        "要",
                        "他",
                        "時",
                        "來",
                        "用",
                        "們",
                        "生",
                        "到",
                        "作",
                        "地",
                        "於",
                        "出",
                        "就",
                        "分",
                        "對",
                        "成",
                        "會",
                        "可",
                        "主",
                        "發",
                        "年",
                        "動",
                        "同",
                        "工",
                        "也",
                        "能",
                        "下",
                        "過",
                        "子",
                        "說",
                        "產",
                        "種",
                        "面",
                        "而",
                        "方",
                        "後",
                        "多",
                        "定",
                        "行",
                        "學",
                        "法",
                        "所",
                        "民",
                        "得",
                        "經",
                        "十",
                        "三",
                        "之",
                        "進",
                        "著",
                        "等",
                        "部",
                        "度",
                        "家",
                        "電",
                        "力",
                        "裡",
                        "如",
                        "水",
                        "化",
                        "高",
                        "自",
                        "二",
                        "理",
                        "起",
                        "小",
                        "物",
                        "現",
                        "實",
                        "加",
                        "量",
                        "都",
                        "兩",
                        "體",
                        "制",
                        "機",
                        "當",
                        "使",
                        "點",
                        "從",
                        "業",
                        "本",
                        "去",
                        "把",
                        "性",
                        "好",
                        "應",
                        "開",
                        "它",
                        "合",
                        "還",
                        "因",
                        "由",
                        "其",
                        "些",
                        "然",
                        "前",
                        "外",
                        "天",
                        "政",
                        "四",
                        "日",
                        "那",
                        "社",
                        "義",
                        "事",
                        "平",
                        "形",
                        "相",
                        "全",
                        "表",
                        "間",
                        "樣",
                        "與",
                        "關",
                        "各",
                        "重",
                        "新",
                        "線",
                        "內",
                        "數",
                        "正",
                        "心",
                        "反",
                        "你",
                        "明",
                        "看",
                        "原",
                        "又",
                        "麼",
                        "利",
                        "比",
                        "或",
                        "但",
                        "質",
                        "氣",
                        "第",
                        "向",
                        "道",
                        "命",
                        "此",
                        "變",
                        "條",
                        "只",
                        "沒",
                        "結",
                        "解",
                        "問",
                        "意",
                        "建",
                        "月",
                        "公",
                        "無",
                        "系",
                        "軍",
                        "很",
                        "情",
                        "者",
                        "最",
                        "立",
                        "代",
                        "想",
                        "已",
                        "通",
                        "並",
                        "提",
                        "直",
                        "題",
                        "黨",
                        "程",
                        "展",
                        "五",
                        "果",
                        "料",
                        "象",
                        "員",
                        "革",
                        "位",
                        "入",
                        "常",
                        "文",
                        "總",
                        "次",
                        "品",
                        "式",
                        "活",
                        "設",
                        "及",
                        "管",
                        "特",
                        "件",
                        "長",
                        "求",
                        "老",
                        "頭",
                        "基",
                        "資",
                        "邊",
                        "流",
                        "路",
                        "級",
                        "少",
                        "圖",
                        "山",
                        "統",
                        "接",
                        "知",
                        "較",
                        "長",
                        "將",
                        "組",
                        "見",
                        "計",
                        "別",
                        "她",
                        "手",
                        "角",
                        "期",
                        "根",
                        "論",
                        "運",
                        "農",
                        "指",
                        "幾",
                        "九",
                        "一",
                        "七",
                        "八",
                        "六",
                        "了",
                        "不",
                        "是",
                        "的",
                        "一",
                        "人",
                        "在",
                        "有",
                        "我",
                        "他",
                        "這",
                        "個",
                        "們",
                        "來",
                        "到",
                        "時",
                        "大",
                        "地",
                        "為",
                        "子",
                        "中",
                        "你",
                        "說",
                        "生",
                        "國",
                        "年",
                        "著",
                        "就",
                        "那",
                        "和",
                        "要",
                        "她",
                        "出",
                        "也",
                        "得",
                        "裡",
                        "後",
                        "自",
                        "以",
                        "會",
                        "家",
                        "可",
                        "下",
                        "而",
                        "過",
                        "天",
                        "去",
                        "能",
                        "對",
                        "小",
                        "多",
                        "然",
                        "於",
                        "心",
                        "學",
                        "麼",
                        "之",
                        "都",
                        "好",
                        "看",
                        "起",
                        "發",
                        "當",
                        "沒",
                        "成",
                        "只",
                        "如",
                        "事",
                        "把",
                        "還",
                        "用",
                        "本",
                        "她",
                        "於",
                        "所",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                        "外",
                        "裡",
                    ]

                    # 計算繁體中文字符比例
                    chinese_char_count = sum(
                        1 for char in text_content if char in traditional_chars
                    )
                    total_chars = len(text_content.replace(" ", "").replace("\n", ""))

                    if total_chars > 0:
                        chinese_ratio = chinese_char_count / total_chars
                        print(
                            f"    嘗試編碼 {encoding}: 中文字符比例 {chinese_ratio:.2%}"
                        )

                        # 如果中文字符比例足夠高，或者有基本的HTML結構
                        if chinese_ratio > 0.1 or (
                            soup.find("html") and len(text_content) > 100
                        ):
                            html_content = decoded_text
                            used_encoding = encoding
                            print(f"    ✓ 使用編碼: {encoding}")
                            break

                except UnicodeDecodeError:
                    print(f"    ✗ 編碼 {encoding} 解碼失敗")
                    continue
                except Exception as e:
                    print(f"    ✗ 編碼 {encoding} 處理錯誤: {e}")
                    continue

            # 如果所有編碼都失敗，嘗試使用 chardet 自動偵測
            if not html_content:
                try:
                    import chardet

                    detected = chardet.detect(raw_content)
                    if detected["encoding"] and detected["confidence"] > 0.7:
                        detected_encoding = detected["encoding"]
                        print(
                            f"    Chardet偵測編碼: {detected_encoding} (信心度: {detected['confidence']:.2%})"
                        )
                        html_content = raw_content.decode(detected_encoding)
                        used_encoding = f"chardet:{detected_encoding}"
                except ImportError:
                    print("    未安裝chardet，跳過自動偵測")
                except Exception as e:
                    print(f"    Chardet偵測失敗: {e}")

            # 最後的fallback
            if not html_content:
                print("    使用UTF-8忽略錯誤模式")
                html_content = raw_content.decode("utf-8", errors="ignore")
                used_encoding = "utf-8(ignore)"

            # 解析HTML獲取標題
            soup = BeautifulSoup(html_content, "html.parser")
            page_title = get_page_title(soup)

            # 生成檔名
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path

            # 使用頁面標題作為檔名，如果沒有則使用URL路徑
            if page_title and page_title != "untitled":
                filename = f"{i:03d}_{sanitize_filename(page_title)}.html"
            else:
                # 使用URL路徑的最後部分
                if path and path != "/":
                    filename = f"{i:03d}_{sanitize_filename(path.split('/')[-1])}.html"
                else:
                    filename = f"{i:03d}_{sanitize_filename(domain)}.html"

            # 確保檔名不為空
            if not filename.endswith(".html"):
                filename = f"{i:03d}_page.html"

            # 保存檔案（確保使用UTF-8編碼保存）
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                # 在檔案開頭加入編碼資訊註解
                f.write(f"<!-- 原始編碼: {used_encoding} -->\n")
                f.write("<!DOCTYPE html>\n")
                # 確保HTML有正確的meta標籤
                if (
                    "<meta charset=" not in html_content.lower()
                    and "<head>" in html_content.lower()
                ):
                    html_content = html_content.replace(
                        "<head>", '<head>\n<meta charset="UTF-8">'
                    )
                elif (
                    "<html>" in html_content.lower()
                    and "<head>" not in html_content.lower()
                ):
                    html_content = html_content.replace(
                        "<html>", '<html>\n<head>\n<meta charset="UTF-8">\n</head>'
                    )
                f.write(html_content)

            print(f"  ✓ 成功下載: {filename}")
            print(f"    編碼: {used_encoding}")
            print(f"    標題: {page_title}")
            print(f"    大小: {len(html_content)} 字元")

            success_count += 1

        except requests.RequestException as e:
            print(f"  ✗ 請求失敗: {e}")
            failed_count += 1
            failed_links.append(url)

        except Exception as e:
            print(f"  ✗ 處理失敗: {e}")
            failed_count += 1
            failed_links.append(url)

        # 延遲避免過於頻繁的請求
        if i < len(links):
            time.sleep(delay)

    # 總結報告
    print(f"\n{'='*50}")
    print(f"下載完成！")
    print(f"成功: {success_count} 個檔案")
    print(f"失敗: {failed_count} 個檔案")
    print(f"檔案保存在: {output_dir}")

    # 保存失敗的連結
    if failed_links:
        failed_file = os.path.join(output_dir, "failed_links.txt")
        with open(failed_file, "w", encoding="utf-8") as f:
            f.write("下載失敗的連結:\n")
            f.write("=" * 30 + "\n")
            for link in failed_links:
                f.write(f"{link}\n")
        print(f"失敗的連結已保存到: {failed_file}")


def create_index_file(output_dir="downloaded_html"):
    """
    建立索引檔案，列出所有下載的HTML檔案

    Args:
        output_dir (str): HTML檔案目錄
    """
    html_files = []

    # 找出所有HTML檔案
    for filename in os.listdir(output_dir):
        if filename.endswith(".html") and filename != "index.html":
            html_files.append(filename)

    # 排序檔案
    html_files.sort()

    # 建立索引HTML
    index_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>下載的HTML檔案索引</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        a {{ text-decoration: none; color: #007bff; }}
        a:hover {{ text-decoration: underline; }}
        .count {{ color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>下載的HTML檔案索引</h1>
    <p class="count">總共 {len(html_files)} 個檔案</p>
    <ul>
"""

    for filename in html_files:
        index_content += (
            f'        <li><a href="{filename}" target="_blank">{filename}</a></li>\n'
        )

    index_content += """    </ul>
</body>
</html>"""

    # 保存索引檔案
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"索引檔案已建立: {index_path}")


# 主程式
if __name__ == "__main__":
    # 設定參數
    input_file = "minlun_links_simple.txt"  # 輸入檔案
    output_directory = "downloaded_html"  # 輸出目錄
    request_delay = 1  # 請求間隔（秒）

    print("開始批量下載HTML檔案...")
    print(f"輸入檔案: {input_file}")
    print(f"輸出目錄: {output_directory}")
    print(f"請求間隔: {request_delay} 秒")

    # 執行下載
    download_html_from_links(input_file, output_directory, request_delay)

    # 建立索引檔案
    create_index_file(output_directory)

    print("\n全部完成！")
