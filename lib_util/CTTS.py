import asyncio
import edge_tts
import os


class TextToSpeechApp:
    def __init__(self):
        self.voices = {
            "1": ("zh-TW-HsiaoChenNeural", "台灣女生 - 小陳"),
            "2": ("zh-TW-YunJheNeural", "台灣男生 - 雲哲"),
            "3": ("zh-CN-XiaoxiaoNeural", "大陸女生 - 曉曉"),
            "4": ("zh-CN-YunxiNeural", "大陸男生 - 雲希"),
            "5": ("en-US-JennyNeural", "英語女生 - Jenny"),
            "6": ("en-US-GuyNeural", "英語男生 - Guy"),
            "7": ("en-US-AnaNeural", "Ana-Cartoon, Conversation  Cute"),
        }
        self.text = ""
        self.selected_voice = ""
        self.output_file = "output.mp3"

    def choose_input_method(self):
        print("\n請選擇文字輸入方式：")
        print("1. 直接輸入文字")
        print("2. 讀取文字檔案")

        choice = input("請輸入選項 (1 或 2): ").strip()

        if choice == "1":
            self.text = input("\n請輸入要轉換的文字:\n").strip()

        elif choice == "2":
            file_path = input("\n請輸入文字檔案路徑: ").strip()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.text = f.read()
                print(f"成功讀取檔案: {file_path}")
            except FileNotFoundError:
                print(f"錯誤: 找不到檔案 {file_path}")
            except Exception as e:
                print(f"讀取檔案時發生錯誤: {e}")
        else:
            print("無效的選項！")

    def choose_voice(self):
        print("\n請選擇語音：")
        for key, (_, desc) in self.voices.items():
            print(f"{key}. {desc}")

        choice = input("請選擇語音 (1-7): ").strip()
        if choice not in self.voices:
            print("無效的語音選項！使用預設語音。")
            choice = "1"

        self.selected_voice = self.voices[choice][0]
        print(f"已選擇: {self.voices[choice][1]}")

    def choose_output_file(self):
        default_output = "output.mp3"
        user_input = input(f"\n請輸入輸出檔案名稱 (預設: {default_output}): ").strip()
        self.output_file = user_input if user_input else default_output

        if not self.output_file.endswith(".mp3"):
            self.output_file += ".mp3"

    async def convert_text_to_speech(self):
        if not self.text:
            print("錯誤: 沒有文字內容可轉換！")
            return

        print(f"\n正在轉換語音...")
        print(f"文字長度: {len(self.text)} 字元")
        print(f"使用語音: {self.selected_voice}")
        print(f"輸出檔案: {self.output_file}")

        try:
            communicate = edge_tts.Communicate(self.text, voice=self.selected_voice)
            await communicate.save(self.output_file)

            file_size = os.path.getsize(self.output_file)
            print(f"\n✅ 轉換完成！")
            print(f"檔案位置: {os.path.abspath(self.output_file)}")
            print(f"檔案大小: {file_size:,} bytes")

        except Exception as e:
            print(f"❌ 轉換失敗: {e}")

    def run(self):
        print("=== 文字轉語音程式 ===")
        self.choose_input_method()
        if not self.text:
            return
        self.choose_voice()
        self.choose_output_file()
        asyncio.run(self.convert_text_to_speech())


def main():
    try:
        app = TextToSpeechApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n程式已中斷。")
    except Exception as e:
        print(f"程式執行錯誤: {e}")


if __name__ == "__main__":
    main()
