from bs4 import BeautifulSoup
import os


def save_as_txt(story, file_path):
    # 只輸出所有段落合成的一段文字
    with open(file_path, "w", encoding="utf-8") as f:
        content = " ".join(story["paragraphs"])
        f.write(content)


def main():
    html_path = input("請輸入 HTML 檔案路徑：").strip()
    output_dir = input("請輸入輸出資料夾路徑：").strip()

    # 確認輸出資料夾存在，不存在就建立
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    story_headers = soup.find_all("h3")
    stories = []

    for header in story_headers:
        story = {
            "title": header.get_text(strip=True),
            "paragraphs": [],
            "image": "",
            "caption": "",
            "source": None,
        }

        next_tag = header.find_next_sibling()
        while next_tag and next_tag.name != "h3":
            if next_tag.name == "figure":
                img = next_tag.find("img")
                if img:
                    story["image"] = img.get("src", "")
                figcaption = next_tag.find("figcaption")
                if figcaption:
                    story["caption"] = figcaption.get_text(strip=True)

            elif next_tag.name == "p":
                text = next_tag.get_text(strip=True)
                if "故事來源：" in text:
                    link = next_tag.find("a")
                    if link:
                        story["source"] = {
                            "text": link.get_text(strip=True),
                            "href": link.get("href", ""),
                        }
                else:
                    story["paragraphs"].append(text)

            next_tag = next_tag.find_next_sibling()

        stories.append(story)

    # 依故事標題建立 txt，內容是段落合併
    for s in stories:
        # 檔名不允許有特殊符號，這裡簡單過濾
        filename = "".join(c for c in s["title"] if c.isalnum() or c in "._- ")
        filename = filename.strip() or "story"
        filepath = os.path.join(output_dir, f"{filename}.txt")
        save_as_txt(s, filepath)
        print(f"已儲存: {filepath}")


if __name__ == "__main__":
    main()
