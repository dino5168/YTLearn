import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin


def fetch_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_content(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")

    # 鎖定內容區域 <div class="rte">
    content_div = soup.find("div", class_="rte")

    # 抓所有圖片網址（絕對化）
    img_urls = []
    if content_div:
        for img in content_div.find_all("img"):
            src = img.get("src", "")
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urljoin(base_url, src)
            img_urls.append(src)

    # 抓所有文字內容
    text_parts = []
    if content_div:
        for p in content_div.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                text_parts.append(text)

    return img_urls, "\n\n".join(text_parts)


def download_images(img_urls, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []

    for i, img_url in enumerate(img_urls, 1):
        try:
            img_name = f"image_{i:02d}" + Path(img_url).suffix.split("?")[0]
            img_path = output_dir / img_name
            response = requests.get(img_url, stream=True)
            response.raise_for_status()

            with open(img_path, "wb") as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)

            saved_paths.append(img_path)
            print(f"✅ 下載圖片：{img_path.name}")
        except Exception as e:
            print(f"❌ 無法下載圖片 {img_url}：{e}")

    return saved_paths


def save_text(text: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / "content.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ 文字已儲存：{text_path}")
    return text_path


def main():
    print("=== 🕷️ 網頁爬蟲工具（圖文版）===")
    url = input("請輸入目標網址：").strip()
    output_dir = Path(input("請輸入輸出資料夾（例如：c:\\temp\\zz）：").strip())

    try:
        print("\n🔍 擷取網頁內容中...")
        html = fetch_page(url)
        img_urls, text = parse_content(html, url)

        # 圖片處理
        if img_urls:
            print(f"\n📸 共找到 {len(img_urls)} 張圖片，開始下載...")
            download_images(img_urls, output_dir)
        else:
            print("⚠️ 找不到圖片")

        # 文字處理
        if text:
            save_text(text, output_dir)
        else:
            print("⚠️ 找不到段落文字")

    except Exception as e:
        print("❌ 發生錯誤：", e)


if __name__ == "__main__":
    main()
