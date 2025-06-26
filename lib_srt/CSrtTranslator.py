import re
from googletrans import Translator


class CSrtTranslator:
    """SRT 字幕翻譯器"""

    def __init__(self):
        """初始化翻譯器"""
        self.translator = Translator()

    def translate_text(self, text, target_lang):
        """翻譯文本

        Args:
            text (str): 要翻譯的文本
            target_lang (str): 目標語言代碼

        Returns:
            str: 翻譯結果
        """
        if not text.strip():
            return ""
        try:
            result = self.translator.translate(text, dest=target_lang)
            return result.text
        except Exception as e:
            print(f"⚠️ 翻譯失敗: {e}")
            return ""

    def process_srt(self, input_path, output_path, target_lang):
        """處理 SRT 檔案翻譯

        Args:
            input_path (str): 輸入檔案路徑
            output_path (str): 輸出檔案路徑
            target_lang (str): 目標語言代碼
        """
        with open(input_path, "r", encoding="utf-8") as infile:
            lines = infile.readlines()

        output_lines = []
        buffer = []
        blocks = []

        # 解析 SRT 區塊
        for line in lines:
            if re.match(r"^\d+$", line.strip()):
                if buffer:
                    blocks.append(list(buffer))
                    buffer.clear()
            buffer.append(line)
        if buffer:
            blocks.append(list(buffer))

        # 處理每個區塊
        total = len(blocks)
        for i, block in enumerate(blocks, start=1):
            output_lines.extend(self._process_block(block, target_lang))
            print(f"⏳ 處理進度: {i}/{total} ({(i/total)*100:.1f}%)", end="\r")

        # 寫入輸出檔案
        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.writelines(output_lines)

    def _process_block(self, block_lines, target_lang):
        """處理單個 SRT 區塊（私有方法）

        Args:
            block_lines (list): 區塊行列表
            target_lang (str): 目標語言代碼

        Returns:
            list: 處理後的行列表
        """
        result = []
        text_lines = []
        block_number = ""
        timecode_line = ""

        for line in block_lines:
            if line.strip().isdigit():
                block_number = line
            elif "-->" in line:
                timecode_line = line
            else:
                text_lines.append(line.strip())

        if text_lines:
            full_text = " ".join(text_lines)
            translated = self.translate_text(full_text, target_lang)
            # 合併為單行字幕
            merged_line = f"{full_text}\n{translated}\n"
            result.extend([block_number, timecode_line, merged_line, "\n"])
        else:
            result.extend(block_lines)
            result.append("\n")

        return result

    def translate_file(self, input_file, output_file, target_lang):
        """翻譯檔案的便捷方法

        Args:
            input_file (str): 輸入檔案路徑
            output_file (str): 輸出檔案路徑
            target_lang (str): 目標語言代碼
        """
        print(f"🚀 開始翻譯至 {target_lang}...")
        self.process_srt(input_file, output_file, target_lang)
        print(f"\n✅ 翻譯完成！已儲存到：{output_file}")


def main():
    """主程式入口"""
    print("🔠 命令列 SRT 翻譯工具（使用 googletrans，不需金鑰）")

    translator = CSrtTranslator()

    input_file = input("📥 請輸入 SRT 檔案路徑（例如：input.srt）：").strip()
    output_file = input("💾 請輸入輸出檔案路徑（例如：output_zh-TW.srt）：").strip()
    lang = input("🌐 請輸入目標語言（例如 zh-TW, ja, fr）：").strip()

    translator.translate_file(input_file, output_file, lang)


if __name__ == "__main__":
    main()
