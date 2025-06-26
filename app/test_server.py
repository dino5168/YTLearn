import os
import requests
from pathlib import Path
import json


def test_thumbnail_service():
    """測試縮圖服務是否正常工作"""

    base_url = "http://127.0.0.1:8000"
    thumbnails_dir = Path("C:/ytdb/thumbnails")

    print("🧪 測試縮圖服務")
    print("=" * 50)

    # 1. 檢查縮圖目錄
    print(f"📁 縮圖目錄: {thumbnails_dir}")
    print(f"📊 目錄存在: {thumbnails_dir.exists()}")

    if thumbnails_dir.exists():
        image_files = (
            list(thumbnails_dir.glob("*.jpg"))
            + list(thumbnails_dir.glob("*.png"))
            + list(thumbnails_dir.glob("*.webp"))
        )
        print(f"🖼️  圖片文件數量: {len(image_files)}")

        for img in image_files[:5]:  # 只顯示前5個
            print(f"   • {img.name} ({img.stat().st_size} bytes)")

    print("\n" + "=" * 50)

    # 2. 測試服務器健康檢查
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 服務器健康檢查通過")
            print(f"   • 縮圖目錄: {health_data.get('thumbnails_dir')}")
            print(f"   • 目錄存在: {health_data.get('thumbnails_exists')}")
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 無法連接到服務器: {e}")
        return

    print("\n" + "=" * 50)

    # 3. 測試縮圖列表 API
    try:
        response = requests.get(f"{base_url}/thumbnails")
        if response.status_code == 200:
            thumbnails_data = response.json()
            print("✅ 縮圖列表 API 正常")
            print(f"   • 縮圖數量: {thumbnails_data.get('count', 0)}")

            for thumb in thumbnails_data.get("thumbnails", [])[:3]:
                print(f"   • {thumb['filename']} - {thumb['size']} bytes")
        else:
            print(f"❌ 縮圖列表 API 失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 縮圖列表 API 錯誤: {e}")

    print("\n" + "=" * 50)

    # 4. 測試單個縮圖訪問
    if thumbnails_dir.exists():
        image_files = list(thumbnails_dir.glob("*.jpg")) + list(
            thumbnails_dir.glob("*.png")
        )

        if image_files:
            test_file = image_files[0]
            print(f"🔍 測試訪問縮圖: {test_file.name}")

            try:
                response = requests.get(f"{base_url}/thumbnails/{test_file.name}")
                if response.status_code == 200:
                    print("✅ 縮圖訪問成功")
                    print(f"   • Content-Type: {response.headers.get('content-type')}")
                    print(
                        f"   • Content-Length: {response.headers.get('content-length')}"
                    )
                    print(f"   • 直接訪問 URL: {base_url}/thumbnails/{test_file.name}")
                else:
                    print(f"❌ 縮圖訪問失敗: {response.status_code}")
            except Exception as e:
                print(f"❌ 縮圖訪問錯誤: {e}")
        else:
            print("⚠️  沒有找到測試用的圖片文件")

    print("\n" + "=" * 50)
    print("🎯 測試完成！")
    print(f"💡 如果一切正常，你可以在瀏覽器中訪問:")
    print(f"    {base_url}/thumbnails")
    print(f"    {base_url}/health")


def create_test_image():
    """創建一個測試圖片（如果目錄為空）"""
    thumbnails_dir = Path("C:/ytdb/thumbnails")
    thumbnails_dir.mkdir(parents=True, exist_ok=True)

    # 檢查是否已有圖片
    existing_images = list(thumbnails_dir.glob("*.jpg")) + list(
        thumbnails_dir.glob("*.png")
    )

    if existing_images:
        print(f"✅ 已有 {len(existing_images)} 個圖片文件")
        return

    # 創建一個簡單的測試圖片 (需要 PIL)
    try:
        from PIL import Image, ImageDraw, ImageFont

        # 創建 320x180 的測試圖片
        img = Image.new("RGB", (320, 180), color="lightblue")
        draw = ImageDraw.Draw(img)

        # 添加文字
        try:
            # 嘗試使用系統字體
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        text = "Test Thumbnail"
        draw.text((10, 80), text, fill="white", font=font)

        # 保存測試圖片
        test_path = thumbnails_dir / "test_thumbnail.jpg"
        img.save(test_path)
        print(f"✅ 創建測試圖片: {test_path}")

    except ImportError:
        print("⚠️  PIL 未安裝，無法創建測試圖片")
        print(
            "   可以手動在 C:/ytdb/thumbnails 目錄下放置一些 .jpg 或 .png 圖片進行測試"
        )


if __name__ == "__main__":
    print("🚀 FastAPI 縮圖服務測試")
    print("請確保 FastAPI 服務器正在運行 (uvicorn server.main:app --reload)")
    print()

    # 創建測試圖片（如果需要）
    create_test_image()
    print()

    # 運行測試
    test_thumbnail_service()
