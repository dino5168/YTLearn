import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


def crawl_table_links(url, output_file="table_links.txt"):
    """
    爬取指定網頁中表格內的所有超連結並保存到文字檔

    Args:
        url (str): 目標網頁URL
        output_file (str): 輸出文字檔名稱
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # 發送請求
        print(f"正在抓取網頁: {url}")
        response = requests.get(url, headers=headers)

        # 嘗試不同編碼
        encodings = ["utf-8", "big5", "gb2312", "gbk"]
        soup = None

        for encoding in encodings:
            try:
                response.encoding = encoding
                soup = BeautifulSoup(response.text, "html.parser")
                # 如果能找到table標籤，說明編碼正確
                if soup.find("table"):
                    print(f"使用編碼: {encoding}")
                    break
            except:
                continue

        if not soup:
            # 如果所有編碼都失敗，使用預設解析
            soup = BeautifulSoup(response.content, "html.parser")

        # 找到所有table標籤
        tables = soup.find_all("table")
        print(f"找到 {len(tables)} 個表格")

        # 收集所有表格內的超連結
        all_links = []

        for i, table in enumerate(tables):
            print(f"處理第 {i+1} 個表格...")

            # 在表格中找到所有a標籤
            links = table.find_all("a", href=True)

            for link in links:
                href = link.get("href")
                text = link.get_text(strip=True)

                # 處理相對路徑
                full_url = urljoin(url, href)

                # 收集連結資訊
                link_info = {"text": text, "url": full_url, "original_href": href}

                all_links.append(link_info)
                print(f"  找到連結: {text} -> {full_url}")

        # 寫入文字檔
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"網頁URL: {url}\n")
            f.write(f"抓取時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"總共找到 {len(all_links)} 個連結\n")
            f.write("=" * 50 + "\n\n")

            for i, link in enumerate(all_links, 1):
                f.write(f"{i}. 連結文字: {link['text']}\n")
                f.write(f"   完整URL: {link['url']}\n")
                f.write(f"   原始href: {link['original_href']}\n")
                f.write("-" * 30 + "\n")

        print(f"\n完成！共找到 {len(all_links)} 個連結")
        print(f"結果已保存到: {output_file}")

        return all_links

    except requests.RequestException as e:
        print(f"請求錯誤: {e}")
        return None
    except Exception as e:
        print(f"處理錯誤: {e}")
        return None


def save_links_simple_format(links, filename="simple_links.txt"):
    """
    將連結以簡單格式保存（每行一個URL）

    Args:
        links (list): 連結列表
        filename (str): 輸出檔名
    """
    if not links:
        print("沒有連結可保存")
        return

    with open(filename, "w", encoding="utf-8") as f:
        for link in links:
            f.write(f"{link['url']}\n")

    print(f"簡單格式連結已保存到: {filename}")


# 主程式
if __name__ == "__main__":
    # 目標網址
    target_url = "https://www.minlun.org.tw/3pt/3-dreamweaver/28.htm"

    # 爬取連結
    links = crawl_table_links(target_url, "minlun_table_links.txt")

    # 如果需要簡單格式的連結清單
    if links:
        save_links_simple_format(links, "minlun_links_simple.txt")

    print("\n執行完成!")
