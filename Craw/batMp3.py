import os
import asyncio
import edge_tts


def read_text_file(file_path):
    """
    讀取文字檔案並返回內容。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {file_path}")
        return None
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {e}")
        return None


def text_to_speech(text, voice, output_file):
    """
    將文字轉換為語音並保存為 MP3 檔案。
    """

    async def convert():
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(output_file)

    asyncio.run(convert())


path = r"C:\temp\佛教故事\Txt"  # 修改成你的資料夾路徑
folder_path = path
files = os.listdir(folder_path)
for file_name in files:
    if file_name.endswith(".txt"):
        file_path = os.path.join(folder_path, file_name)
        print(f"正在處理文件: {file_path}")
        content = read_text_file(file_path)
        # print(content)
        if content is None:
            continue
        output_file = os.path.join(folder_path, f"{os.path.splitext(file_name)[0]}.mp3")

        text_to_speech(
            content,
            "zh-TW-HsiaoChenNeural",  # 選擇語音
            output_file,
        )
        print(f"已保存語音到: {output_file}")
