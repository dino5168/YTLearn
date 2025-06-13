from PIL import Image
import os
import glob


def get_user_input():
    """獲取用戶輸入的參數"""
    print("=== 圖片批量調整大小工具 ===\n")

    # 獲取來源目錄
    while True:
        source_dir = input("請輸入來源圖片目錄路徑: ").strip()
        if os.path.exists(source_dir):
            break
        else:
            print(f"目錄 '{source_dir}' 不存在，請重新輸入！")

    # 獲取目標目錄
    target_dir = input("請輸入目標儲存目錄路徑: ").strip()
    if not os.path.exists(target_dir):
        create_dir = (
            input(f"目錄 '{target_dir}' 不存在，是否要建立？(y/n): ").strip().lower()
        )
        if create_dir == "y" or create_dir == "yes":
            os.makedirs(target_dir, exist_ok=True)
            print(f"已建立目錄: {target_dir}")
        else:
            print("取消操作")
            return None

    # 獲取目標尺寸
    while True:
        try:
            width = int(input("請輸入目標寬度 (預設1792): ").strip() or "1792")
            height = int(input("請輸入目標高度 (預設1024): ").strip() or "1024")
            break
        except ValueError:
            print("請輸入有效的數字！")

    # 獲取圖片格式
    supported_formats = ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]
    print(f"支援的圖片格式: {', '.join(supported_formats)}")
    formats = (
        input("請輸入要處理的圖片格式 (用逗號分隔，預設jpg,png): ").strip() or "jpg,png"
    )
    formats = [f.strip().lower() for f in formats.split(",")]

    return {
        "source_dir": source_dir,
        "target_dir": target_dir,
        "width": width,
        "height": height,
        "formats": formats,
    }


def find_images(source_dir, formats):
    """尋找指定格式的圖片檔案"""
    image_files = []
    for fmt in formats:
        pattern = os.path.join(source_dir, f"*.{fmt}")
        image_files.extend(glob.glob(pattern, recursive=False))
        # 也搜尋大寫副檔名
        pattern = os.path.join(source_dir, f"*.{fmt.upper()}")
        image_files.extend(glob.glob(pattern, recursive=False))

    return list(set(image_files))  # 去除重複


def resize_image(input_path, output_path, width, height):
    """調整單張圖片大小"""
    try:
        with Image.open(input_path) as img:
            # 轉換為RGB模式（避免某些格式的問題）
            if img.mode != "RGB":
                img = img.convert("RGB")

            # 調整大小
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)

            # 儲存
            resized_img.save(output_path, "JPEG", quality=95)
            return True
    except Exception as e:
        print(f"處理 {input_path} 時發生錯誤: {e}")
        return False


def main():
    """主程式"""
    # 獲取用戶輸入
    config = get_user_input()
    if not config:
        return

    # 尋找圖片檔案
    print(f"\n正在搜尋 {config['source_dir']} 中的圖片...")
    image_files = find_images(config["source_dir"], config["formats"])

    if not image_files:
        print("未找到任何符合條件的圖片檔案！")
        return

    print(f"找到 {len(image_files)} 張圖片")

    # 顯示找到的檔案
    print("\n找到的圖片檔案：")
    for i, file in enumerate(image_files, 1):
        filename = os.path.basename(file)
        print(f"{i:2d}. {filename}")

    # 確認是否繼續
    confirm = (
        input(
            f"\n是否要將這些圖片調整為 {config['width']}x{config['height']} 並儲存到 {config['target_dir']}？(y/n): "
        )
        .strip()
        .lower()
    )
    if confirm not in ["y", "yes"]:
        print("取消操作")
        return

    # 批量處理
    print(f"\n開始處理...")
    success_count = 0

    for i, input_path in enumerate(image_files, 1):
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_resized.jpg"  # 統一輸出為jpg格式
        output_path = os.path.join(config["target_dir"], output_filename)

        print(f"({i}/{len(image_files)}) 處理中: {filename}")

        if resize_image(input_path, output_path, config["width"], config["height"]):
            success_count += 1
            print(f"  ✓ 已儲存: {output_filename}")
        else:
            print(f"  ✗ 處理失敗: {filename}")

    print(f"\n=== 處理完成 ===")
    print(f"成功處理: {success_count}/{len(image_files)} 張圖片")
    print(f"儲存位置: {config['target_dir']}")


if __name__ == "__main__":
    main()
