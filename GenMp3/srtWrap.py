import textwrap
import os
import re


def wrap_srt_line(text, width=42):
    """將文字按指定寬度換行"""
    if not text.strip():
        return ""
    return "\n".join(textwrap.wrap(text.strip(), width=width))


def is_timestamp_line(line):
    """檢查是否為時間戳記行"""
    return "-->" in line


def is_subtitle_number(line):
    """檢查是否為字幕序號"""
    return line.strip().isdigit()


def reformat_srt(input_path, output_path, max_line_width=42):
    """
    重新格式化 SRT 字幕文件

    Args:
        input_path: 輸入文件路徑
        output_path: 輸出文件路徑
        max_line_width: 每行最大字符數
    """
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"❌ 找不到文件: {input_path}")
        return False
    except Exception as e:
        print(f"❌ 讀取文件時發生錯誤: {e}")
        return False

    # 按空行分割字幕塊
    subtitle_blocks = re.split(r"\n\s*\n", content.strip())
    formatted_blocks = []

    for block in subtitle_blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        if len(lines) < 3:  # 至少需要序號、時間戳、內容
            formatted_blocks.append(block)
            continue

        # 分離序號、時間戳和字幕內容
        subtitle_num = lines[0]
        timestamp = lines[1]
        subtitle_text = " ".join(lines[2:]).strip()

        # 格式化字幕內容
        wrapped_text = wrap_srt_line(subtitle_text, max_line_width)

        # 重組字幕塊
        formatted_block = f"{subtitle_num}\n{timestamp}\n{wrapped_text}"
        formatted_blocks.append(formatted_block)

    # 寫入輸出文件
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n\n".join(formatted_blocks) + "\n")
        print(f"✅ 成功處理字幕文件: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 寫入文件時發生錯誤: {e}")
        return False


def interactive_mode():
    """交談式模式"""
    print("🎬 SRT 字幕格式化工具")
    print("=" * 50)

    while True:
        print("\n選擇操作:")
        print("1. 格式化字幕文件")
        print("2. 批量處理資料夾")
        print("3. 設定說明")
        print("4. 退出")

        choice = input("\n請輸入選項 (1-4): ").strip()

        if choice == "1":
            single_file_mode()
        elif choice == "2":
            batch_mode()
        elif choice == "3":
            show_help()
        elif choice == "4":
            print("👋 再見!")
            break
        else:
            print("❌ 無效選項，請重新輸入")


def single_file_mode():
    """單文件處理模式"""
    print("\n📁 單文件處理模式")

    # 輸入文件路徑
    input_path = input("請輸入 SRT 文件路徑: ").strip()
    if not input_path:
        print("❌ 請輸入有效的文件路徑")
        return

    if not os.path.exists(input_path):
        print(f"❌ 文件不存在: {input_path}")
        return

    # 輸出文件路徑
    default_output = input_path.replace(".srt", "_formatted.srt")
    output_path = input(f"輸出文件路徑 (預設: {default_output}): ").strip()
    if not output_path:
        output_path = default_output

    # 行寬設定
    try:
        width = input("每行最大字符數 (預設: 42): ").strip()
        max_width = int(width) if width else 42
        if max_width <= 0:
            raise ValueError
    except ValueError:
        print("❌ 無效的行寬設定，使用預設值 42")
        max_width = 42

    # 執行格式化
    print(f"\n🔄 正在處理文件...")
    success = reformat_srt(input_path, output_path, max_width)

    if success:
        print(f"📊 處理完成！")
        print(f"   輸入: {input_path}")
        print(f"   輸出: {output_path}")
        print(f"   行寬: {max_width} 字符")


def batch_mode():
    """批量處理模式"""
    print("\n📂 批量處理模式")

    folder_path = input("請輸入包含 SRT 文件的資料夾路徑: ").strip()
    if not folder_path or not os.path.exists(folder_path):
        print("❌ 資料夾不存在")
        return

    # 行寬設定
    try:
        width = input("每行最大字符數 (預設: 42): ").strip()
        max_width = int(width) if width else 42
        if max_width <= 0:
            raise ValueError
    except ValueError:
        print("❌ 無效的行寬設定，使用預設值 42")
        max_width = 42

    # 尋找 SRT 文件
    srt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".srt")]

    if not srt_files:
        print("❌ 資料夾中沒有找到 SRT 文件")
        return

    print(f"\n找到 {len(srt_files)} 個 SRT 文件:")
    for i, file in enumerate(srt_files, 1):
        print(f"  {i}. {file}")

    confirm = input(f"\n是否處理這些文件? (y/n): ").strip().lower()
    if confirm not in ["y", "yes", "是"]:
        print("❌ 取消處理")
        return

    # 批量處理
    success_count = 0
    for file in srt_files:
        input_path = os.path.join(folder_path, file)
        output_path = os.path.join(folder_path, file.replace(".srt", "_formatted.srt"))

        print(f"🔄 處理: {file}")
        if reformat_srt(input_path, output_path, max_width):
            success_count += 1

    print(f"\n📊 批量處理完成！成功處理 {success_count}/{len(srt_files)} 個文件")


def show_help():
    """顯示說明"""
    help_text = """
📖 使用說明

🎯 功能:
• 自動調整 SRT 字幕每行的字符數
• 保持字幕的時間戳和序號不變
• 支援單文件和批量處理

⚙️ 設定:
• 行寬: 建議 35-50 字符 (中文約 17-25 字)
• 編碼: 自動處理 UTF-8 編碼
• 輸出: 原文件名 + '_formatted' 後綴

💡 使用技巧:
• 較短的行寬適合手機觀看
• 較長的行寬適合電腦觀看
• 建議先用小範圍測試效果

📝 支援格式:
標準 SRT 格式:
1
00:00:01,000 --> 00:00:03,000
字幕內容

⚠️ 注意事項:
• 請備份原始文件
• 確保文件為 UTF-8 編碼
• 檢查處理後的時間軸是否正確
"""
    print(help_text)


if __name__ == "__main__":
    # 可以直接調用函數或使用交談式模式

    # 直接使用範例:
    # reformat_srt("input.srt", "output_formatted.srt", max_line_width=42)

    # 交談式模式:
    interactive_mode()
