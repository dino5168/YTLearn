from moviepy.editor import VideoFileClip
import os


def mp4_to_mp3(mp4_file, mp3_file=None):
    """
    將 MP4 檔案的音訊轉換為 MP3

    參數:
    mp4_file: 輸入的 MP4 檔案路徑
    mp3_file: 輸出的 MP3 檔案路徑 (可選，預設會自動生成)
    """
    try:
        # 如果沒有指定輸出檔案名稱，自動生成
        if mp3_file is None:
            base_name = os.path.splitext(mp4_file)[0]
            mp3_file = f"{base_name}.mp3"

        print(f"正在處理: {mp4_file}")
        print(f"輸出檔案: {mp3_file}")

        # 載入影片檔案
        video = VideoFileClip(mp4_file)

        # 提取音訊
        audio = video.audio

        # 寫入 MP3 檔案
        print("正在轉換音訊...")
        audio.write_audiofile(mp3_file, verbose=False, logger=None)

        # 關閉檔案以釋放資源
        audio.close()
        video.close()

        print(f"轉換完成！MP3 檔案已儲存至: {mp3_file}")
        return True

    except Exception as e:
        print(f"轉換失敗: {str(e)}")
        return False


def batch_convert(input_folder, output_folder=None):
    """
    批次轉換資料夾中的所有 MP4 檔案

    參數:
    input_folder: 包含 MP4 檔案的資料夾
    output_folder: 輸出資料夾 (可選)
    """
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    mp4_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".mp4")]

    if not mp4_files:
        print("在指定資料夾中找不到 MP4 檔案")
        return

    print(f"找到 {len(mp4_files)} 個 MP4 檔案")

    for i, filename in enumerate(mp4_files, 1):
        print(f"\n處理第 {i}/{len(mp4_files)} 個檔案:")

        input_path = os.path.join(input_folder, filename)

        if output_folder:
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, f"{base_name}.mp3")
        else:
            output_path = None

        mp4_to_mp3(input_path, output_path)


def show_menu():
    """顯示選單"""
    print("\n" + "=" * 50)
    print("        MP4 轉 MP3 轉換器")
    print("=" * 50)
    print("1. 單一檔案轉換")
    print("2. 批次轉換（整個資料夾）")
    print("3. 退出程式")
    print("=" * 50)


def get_user_choice():
    """獲取使用者選擇"""
    while True:
        try:
            choice = input("請選擇功能 (1-3): ").strip()
            if choice in ["1", "2", "3"]:
                return int(choice)
            else:
                print("請輸入 1、2 或 3")
        except KeyboardInterrupt:
            print("\n程式已取消")
            return 3


def single_file_convert():
    """單一檔案轉換"""
    print("\n--- 單一檔案轉換 ---")

    # 獲取輸入檔案路徑
    while True:
        mp4_file = input("請輸入 MP4 檔案路徑: ").strip()
        if not mp4_file:
            print("路徑不能為空，請重新輸入")
            continue

        if not os.path.exists(mp4_file):
            print(f"找不到檔案: {mp4_file}")
            retry = input("是否重新輸入？(y/n): ").strip().lower()
            if retry != "y":
                return
            continue

        if not mp4_file.lower().endswith(".mp4"):
            print("請確保檔案是 MP4 格式")
            retry = input("是否重新輸入？(y/n): ").strip().lower()
            if retry != "y":
                return
            continue

        break

    # 獲取輸出檔案路徑（可選）
    mp3_file = input("請輸入輸出 MP3 檔案路徑 (直接按 Enter 自動生成): ").strip()
    if not mp3_file:
        mp3_file = None

    # 執行轉換
    success = mp4_to_mp3(mp4_file, mp3_file)

    if success:
        print("\n✅ 轉換成功！")
    else:
        print("\n❌ 轉換失敗！")


def batch_file_convert():
    """批次檔案轉換"""
    print("\n--- 批次檔案轉換 ---")

    # 獲取輸入資料夾路徑
    while True:
        input_folder = input("請輸入包含 MP4 檔案的資料夾路徑: ").strip()
        if not input_folder:
            print("路徑不能為空，請重新輸入")
            continue

        if not os.path.exists(input_folder):
            print(f"找不到資料夾: {input_folder}")
            retry = input("是否重新輸入？(y/n): ").strip().lower()
            if retry != "y":
                return
            continue

        if not os.path.isdir(input_folder):
            print("請輸入有效的資料夾路徑")
            retry = input("是否重新輸入？(y/n): ").strip().lower()
            if retry != "y":
                return
            continue

        break

    # 獲取輸出資料夾路徑（可選）
    output_folder = input(
        "請輸入輸出資料夾路徑 (直接按 Enter 輸出到原資料夾): "
    ).strip()
    if not output_folder:
        output_folder = None

    # 確認執行
    mp4_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".mp4")]
    if not mp4_files:
        print("在指定資料夾中找不到 MP4 檔案")
        return

    print(f"\n找到 {len(mp4_files)} 個 MP4 檔案:")
    for i, filename in enumerate(mp4_files, 1):
        print(f"  {i}. {filename}")

    confirm = (
        input(f"\n確定要轉換這 {len(mp4_files)} 個檔案嗎？(y/n): ").strip().lower()
    )
    if confirm != "y":
        print("已取消轉換")
        return

    # 執行批次轉換
    batch_convert(input_folder, output_folder)
    print("\n✅ 批次轉換完成！")


def main():
    """主程式"""
    print("歡迎使用 MP4 轉 MP3 轉換器！")

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == 1:
            single_file_convert()
        elif choice == 2:
            batch_file_convert()
        elif choice == 3:
            print("\n謝謝使用，再見！")
            break

        # 詢問是否繼續
        if choice in [1, 2]:
            continue_choice = input("\n是否繼續使用？(y/n): ").strip().lower()
            if continue_choice != "y":
                print("謝謝使用，再見！")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已被使用者中斷，再見！")
