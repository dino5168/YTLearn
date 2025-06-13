import requests


def download_html(url: str, filename: str = "output.html"):
    try:
        response = requests.get(url)
        response.encoding = "big5"  # 設定為 big5 編碼，因為這個網站是使用 big5 編碼
        # 如果網站有提供其他編碼，可以根據需要調整這裡的編碼設定

        response.raise_for_status()

        detected_encoding = "big5"  # 這個網站確定是 big5 編碼
        print(f"使用編碼：{detected_encoding}")

        html_text = response.content.decode(detected_encoding, errors="ignore")

        with open(filename, "w", encoding="big5") as file:
            file.write(html_text)

    except requests.exceptions.RequestException as e:
        print(f"下載失敗：{e}")
    except UnicodeDecodeError as e:
        print(f"編碼錯誤：{e}")


if __name__ == "__main__":
    url = "https://www.minlun.org.tw/3pt/3pt-1-7/t/113.htm?"
    download_html(url)
