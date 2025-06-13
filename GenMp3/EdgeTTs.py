import asyncio
import edge_tts
import os


async def text_to_speech():
    print("=== 文字轉語音程式 ===")

    # Step 1: 讓使用者選擇輸入方式
    print("\n請選擇文字輸入方式：")
    print("1. 直接輸入文字")
    print("2. 讀取文字檔案")

    choice = input("請輸入選項 (1 或 2): ").strip()

    text = ""

    if choice == "1":
        # 直接輸入文字
        print("\n請輸入要轉換的文字 (輸入完成後按 Enter):")
        text = input().strip()

    elif choice == "2":
        # 讀取檔案
        file_path = input("\n請輸入文字檔案路徑: ").strip()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            print(f"成功讀取檔案: {file_path}")
        except FileNotFoundError:
            print(f"錯誤: 找不到檔案 {file_path}")
            return
        except Exception as e:
            print(f"讀取檔案時發生錯誤: {e}")
            return
    else:
        print("無效的選項！")
        return

    if not text:
        print("錯誤: 沒有文字內容可轉換！")
        return

    # Step 2: 選擇語音
    print("\n請選擇語音：")
    voices = {
        "1": ("zh-TW-HsiaoChenNeural", "台灣女生 - 小陳"),
        "2": ("zh-TW-YunJheNeural", "台灣男生 - 雲哲"),
        "3": ("zh-CN-XiaoxiaoNeural", "大陸女生 - 曉曉"),
        "4": ("zh-CN-YunxiNeural", "大陸男生 - 雲希"),
        "5": ("en-US-JennyNeural", "英語女生 - Jenny"),
        "6": ("en-US-GuyNeural", "英語男生 - Guy"),
        "7": ("en-US-AnaNeural", "Ana-Cartoon, Conversation  Cute"),
    }

    for key, (_, desc) in voices.items():
        print(f"{key}. {desc}")

    voice_choice = input("請選擇語音 (1-6): ").strip()

    if voice_choice not in voices:
        print("無效的語音選項！使用預設語音。")
        voice_choice = "1"

    selected_voice = voices[voice_choice][0]
    print(f"已選擇: {voices[voice_choice][1]}")

    # Step 3: 設定輸出檔案
    default_output = "output.mp3"
    output_file = input(f"\n請輸入輸出檔案名稱 (預設: {default_output}): ").strip()

    if not output_file:
        output_file = default_output

    # 確保檔案有 .mp3 副檔名
    if not output_file.endswith(".mp3"):
        output_file += ".mp3"

    # Step 4: 轉換語音
    print(f"\n正在轉換語音...")
    print(f"文字長度: {len(text)} 字元")
    print(f"使用語音: {voices[voice_choice][1]}")
    print(f"輸出檔案: {output_file}")

    try:
        communicate = edge_tts.Communicate(text, voice=selected_voice)
        await communicate.save(output_file)

        # 顯示檔案資訊
        file_size = os.path.getsize(output_file)
        print(f"\n✅ 轉換完成！")
        print(f"檔案位置: {os.path.abspath(output_file)}")
        print(f"檔案大小: {file_size:,} bytes")

    except Exception as e:
        print(f"❌ 轉換失敗: {e}")


def main():
    try:
        asyncio.run(text_to_speech())
    except KeyboardInterrupt:
        print("\n\n程式已中斷。")
    except Exception as e:
        print(f"程式執行錯誤: {e}")


if __name__ == "__main__":
    main()
