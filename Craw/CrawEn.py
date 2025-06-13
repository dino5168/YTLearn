import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def scrape_monkeypen_story(url, output_dir=None, text_file=None):
    """
    從指定 URL 抓取 HTML，提取故事文字與圖片。

    Args:
        url: 目標網址
        output_dir: 圖片輸出資料夾名稱 (預設: images)
        text_file: 文字檔案名稱 (預設: story.txt)
    """
    # 使用預設值或使用者輸入的值
    if not output_dir:
        output_dir = "images"
    if not text_file:
        text_file = "story.txt"

    # 建立 images 資料夾 (如果不存在)
    os.makedirs(output_dir, exist_ok=True)
    print(f"資料夾 '{output_dir}' 已準備就緒。")

    # 嘗試抓取 HTML 網頁內容
    try:
        print(f"正在讀取網頁：{url}")
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
    except requests.exceptions.RequestException as e:
        print(f"錯誤：無法讀取網頁內容 {url}。 {e}")
        return

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, "html.parser")

    # --- 1. 提取並儲存故事文字 ---
    article_content = soup.find("div", class_="article__content")

    story_paragraphs = []
    if article_content:
        paragraphs = article_content.find_all("p")

        stop_phrases = [
            "illegal to use this free children's book",
            "Please share our books",
            "Click here to read more",
        ]

        for p in paragraphs:
            text = p.get_text(strip=True, separator=" ")
            if text and not any(phrase in text for phrase in stop_phrases):
                story_paragraphs.append(text)

    full_story = "\n\n".join(story_paragraphs)

    try:
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(full_story)
        print(f"故事已成功儲存至 '{text_file}'。")
    except IOError as e:
        print(f"錯誤：無法寫入檔案 {text_file}。 {e}")

    # --- 2. 提取並下載圖片 ---
    if article_content:
        images = article_content.find_all("img", alt="Free Children's Book")

        print(f"\n找到 {len(images)} 張故事圖片，開始下載...")

        for idx, img in enumerate(images):
            img_src = img.get("src")

            if not img_src:
                continue

            if img_src.startswith("//"):
                img_url = "https:" + img_src
            else:
                img_url = urljoin(url, img_src)

            try:
                path = urlparse(img_url).path
                filename = os.path.basename(path)

                name, ext = os.path.splitext(filename)
                unique_filename = f"{idx+1:02d}_{name}{ext}"

                filepath = os.path.join(output_dir, unique_filename)

                img_response = requests.get(img_url, stream=True)
                img_response.raise_for_status()

                with open(filepath, "wb") as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"  ({idx+1}/{len(images)}) 已下載: {unique_filename}")

            except requests.exceptions.RequestException as e:
                print(f"  下載失敗: {img_url} ({e})")
            except IOError as e:
                print(f"  儲存失敗: {unique_filename} ({e})")

    print("\n所有任務完成！")


def get_user_input():
    """
    交談式取得使用者輸入參數
    """
    print("=== Monkey Pen 故事爬蟲程式 ===\n")

    # 取得網址
    while True:
        url = input("請輸入故事網址 (或按 Enter 使用預設網址): ").strip()
        if not url:
            url = "https://monkeypen.com/blogs/news/hide-and-seek-free-childrens-book-from-monkey-pen"
            print(f"使用預設網址: {url}")
            break
        elif url.startswith("http"):
            break
        else:
            print("請輸入有效的網址 (需以 http 或 https 開頭)")

    # 取得圖片資料夾名稱
    output_dir = input("\n請輸入圖片資料夾名稱 (預設: images): ").strip()
    if not output_dir:
        output_dir = "images"

    # 取得文字檔案名稱
    text_file = input("請輸入文字檔案名稱 (預設: story.txt): ").strip()
    if not text_file:
        text_file = "story.txt"

    # 確認設定
    print(f"\n=== 確認設定 ===")
    print(f"網址: {url}")
    print(f"圖片資料夾: {output_dir}")
    print(f"文字檔案: {text_file}")

    confirm = input("\n確認開始執行嗎？(y/N): ").strip().lower()
    if confirm in ["y", "yes", "是"]:
        return url, output_dir, text_file
    else:
        print("已取消執行。")
        return None, None, None


def main():
    """
    主程式，提供多種執行方式
    """
    print("選擇執行模式：")
    print("1. 交談式輸入參數")
    print("2. 使用預設參數快速執行")
    print("3. 自訂參數執行")

    choice = input("\n請選擇 (1-3): ").strip()

    if choice == "1":
        # 交談式輸入
        url, output_dir, text_file = get_user_input()
        if url:
            scrape_monkeypen_story(url, output_dir, text_file)

    elif choice == "2":
        # 使用預設參數
        print("\n使用預設參數執行...")
        default_url = "https://monkeypen.com/blogs/news/hide-and-seek-free-childrens-book-from-monkey-pen"
        scrape_monkeypen_story(default_url)

    elif choice == "3":
        # 自訂參數 (可以直接在這裡修改)
        custom_url = input("請輸入網址: ").strip()
        custom_output_dir = input("請輸入圖片資料夾名稱: ").strip() or "images"
        custom_text_file = input("請輸入文字檔案名稱: ").strip() or "story.txt"

        if custom_url:
            scrape_monkeypen_story(custom_url, custom_output_dir, custom_text_file)
        else:
            print("網址不能為空！")

    else:
        print("無效的選擇，程式結束。")


if __name__ == "__main__":
    main()
