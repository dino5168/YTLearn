import os
import subprocess
from pathlib import Path
from pysubs2 import SSAFile, SSAStyle, Color
from typing import Optional
import sys


def ask_path(prompt, must_exist=True, is_file=False):
    """交談式路徑輸入函數"""
    while True:
        path = input(prompt).strip('" ')
        if not path:
            print("⚠️ 請輸入有效路徑。")
            continue
            
        p = Path(path)
        
        if must_exist and not p.exists():
            print("❌ 找不到路徑，請重新輸入。")
        elif is_file and not p.is_file():
            print("❌ 請指定一個檔案而不是資料夾。")
        elif is_file and p.is_dir():
            print("❌ 請指定檔案而不是資料夾。")
        else:
            return p


def check_dependencies():
    """檢查必要的依賴項目"""
    print("🔍 檢查系統依賴...")
    
    # 檢查 FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg 已安裝")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到 FFmpeg，請先安裝 FFmpeg")
        print("   下載網址：https://ffmpeg.org/download.html")
        return False
    
    # 檢查 pysubs2
    try:
        import pysubs2
        print("✅ pysubs2 已安裝")
    except ImportError:
        print("❌ 未找到 pysubs2，請執行：pip install pysubs2")
        return False
    
    return True


def convert_srt_to_ass(srt_path: Path, output_path: Path):
    """將 SRT 字幕轉換為 ASS 格式並套用雙語樣式"""
    try:
        subs = SSAFile.load(str(srt_path), encoding="utf-8")
        
        # 預設樣式（英文 - 白色）
        default_style = SSAStyle()
        default_style.fontname = "Arial"
        default_style.fontsize = 20  # 縮小字體
        default_style.primarycolor = Color(255, 255, 255)  # 白色
        default_style.secondarycolor = Color(255, 255, 255)
        default_style.outlinecolor = Color(0, 0, 0)  # 黑色外框
        default_style.backcolor = Color(0, 0, 0)
        default_style.bold = False
        default_style.outline = 2
        default_style.shadow = 1
        default_style.alignment = 2  # 中下對齊
        
        # 中文樣式（中文 - 黃色）
        chinese_style = SSAStyle()
        chinese_style.fontname = "Microsoft YaHei"  # 中文字體
        chinese_style.fontsize = 18  # 中文稍微小一點
        chinese_style.primarycolor = Color(255, 255, 0)  # 黃色
        chinese_style.secondarycolor = Color(255, 255, 0)
        chinese_style.outlinecolor = Color(0, 0, 0)  # 黑色外框
        chinese_style.backcolor = Color(0, 0, 0)
        chinese_style.bold = False
        chinese_style.outline = 2
        chinese_style.shadow = 1
        chinese_style.alignment = 2  # 中下對齊
        
        subs.styles["Default"] = default_style
        subs.styles["Chinese"] = chinese_style
        
        # 處理每一行字幕，分離英文和中文
        for line in subs:
            text = line.text
            # 檢查是否包含中文字符
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                # 如果有中文，分離英文和中文
                lines = text.split('\n')
                if len(lines) >= 2:
                    # 假設第一行是英文，第二行是中文
                    english_line = lines[0].strip()
                    chinese_line = lines[1].strip()
                    
                    # 重新組合：英文用預設樣式，中文用黃色樣式
                    line.text = f"{english_line}\\N{{\\rChinese}}{chinese_line}"
                else:
                    # 只有一行，檢查是否為中文
                    if any('\u4e00' <= char <= '\u9fff' for char in text):
                        line.text = f"{{\\rChinese}}{text}"
        
        subs.save(str(output_path))
        print(f"✅ 字幕轉換完成：{output_path.name}")
        print("   - 英文：白色 20pt")
        print("   - 中文：黃色 18pt")
        return output_path
    except Exception as e:
        print(f"❌ 字幕轉換失敗：{e}")
        return None


def generate_video(mp3_file: Path, ass_path: Path, output_dir: Path, bg_image: Optional[Path]):
    """生成影片"""
    output_file = output_dir / f"{mp3_file.stem}.mp4"
    
    # 驗證輸入檔案
    if not mp3_file.exists():
        print(f"❌ MP3 檔案不存在：{mp3_file}")
        return False
    
    if not ass_path.exists():
        print(f"❌ 字幕檔案不存在：{ass_path}")
        return False
    
    # 準備背景輸入
    if bg_image and bg_image.exists() and bg_image.is_file():
        bg_input = ["-loop", "1", "-i", str(bg_image)]
        print(f"📷 使用背景圖：{bg_image.name}")
    else:
        bg_input = ["-f", "lavfi", "-i", "color=c=black:s=1280x720"]
        print("⬛ 使用黑色背景")
        if bg_image:
            print(f"⚠️ 背景圖片問題：{bg_image} (不存在或不是檔案)")
    
    # 構建 FFmpeg 命令 - 使用更兼容的編碼設定
    ass_path_escaped = str(ass_path).replace("\\", "\\\\").replace(":", "\\:")
    
    cmd = [
        "ffmpeg",
        *bg_input,
        "-i", str(mp3_file),
        "-vf", f"subtitles='{ass_path_escaped}'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",  # 確保兼容性
        "-profile:v", "baseline",  # 使用基線 profile 提高兼容性
        "-level", "3.0",  # 設定 H.264 level
        "-movflags", "+faststart",  # 優化網頁播放
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",  # 標準音訊採樣率
        "-ac", "2",  # 立體聲
        "-shortest",
        "-y",
        str(output_file)
    ]
    
    print(f"🎞️ 正在處理：{mp3_file.name} -> {output_file.name}")
    
    # 除錯資訊
    print("🔍 除錯資訊：")
    print(f"   MP3: {mp3_file}")
    print(f"   字幕: {ass_path}")
    print(f"   背景: {bg_image if bg_image else '黑色背景'}")
    print(f"   輸出: {output_file}")
    print(f"   FFmpeg 命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 完成：{output_file.name}")
            return True
        else:
            print(f"❌ FFmpeg 錯誤 (返回碼: {result.returncode})：")
            print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
    except Exception as e:
        print(f"❌ 執行錯誤：{e}")
        return False


def main():
    """主程式"""
    print("🎬 MP3 + 字幕合併 MP4 工具")
    print("════════════════════════════════════")
    print("功能：將 MP3 音檔和 SRT 字幕合併成 MP4 影片")
    print("支援：自動配對同名背景圖片或使用預設背景")
    print("════════════════════════════════════\n")
    
    # 檢查依賴
    if not check_dependencies():
        input("\n按 Enter 鍵結束...")
        return
    
    print()
    
    try:
        # 1. 取得 MP3 資料夾
        mp3_dir = ask_path("📁 請輸入 MP3 資料夾路徑：", must_exist=True)
        
        # 2. 取得 SRT 字幕檔
        srt_path = ask_path("📝 請輸入 SRT 字幕檔路徑：", must_exist=True, is_file=True)
        
        # 3. 尋找目錄中的所有圖片作為預設背景
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]
        all_images = []
        for ext in image_extensions:
            all_images.extend(mp3_dir.glob(f"*{ext}"))
        
        # 按檔名排序，取最後一張作為預設背景
        fallback_image = None
        if all_images:
            fallback_image = sorted(all_images)[-1]
            print(f"🖼️ 找到 {len(all_images)} 張圖片，預設背景：{fallback_image.name}")
        else:
            print("⚠️ 目錄中沒有圖片，將使用純色背景。")
        
        # 4. 輸出資料夾
        output_dir = ask_path("📂 請輸入輸出資料夾路徑：", must_exist=False)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 5. 轉換字幕格式
        print(f"\n🔄 轉換字幕格式...")
        ass_path = output_dir / (srt_path.stem + ".ass")
        if not convert_srt_to_ass(srt_path, ass_path):
            print("❌ 字幕轉換失敗，程式結束。")
            return
        
        # 6. 尋找所有 MP3 檔案
        mp3_files = sorted(mp3_dir.glob("*.mp3"))
        if not mp3_files:
            print("❌ 沒有找到 MP3 檔案！請確認路徑。")
            return
        
        print(f"\n🔍 找到 {len(mp3_files)} 個 MP3 檔案，開始處理...\n")
        
        # 7. 批次處理
        success_count = 0
        for i, mp3_file in enumerate(mp3_files, 1):
            print(f"[{i}/{len(mp3_files)}] 處理：{mp3_file.name}")
            
            # 尋找對應的背景圖片（優先同名圖片）
            matched_image = None
            
            # 首先尋找同名圖片
            for ext in image_extensions:
                candidate = mp3_file.with_suffix(ext)
                if candidate.exists():
                    matched_image = candidate
                    print(f"📷 找到同名背景：{matched_image.name}")
                    break
            
            # 如果沒有同名圖片，使用目錄中最後一張圖片
            if not matched_image:
                matched_image = fallback_image
                if matched_image:
                    print(f"🖼️ 使用預設背景：{matched_image.name}")
                else:
                    print("⬛ 使用純色背景")
            
            # 生成影片
            if generate_video(mp3_file, ass_path, output_dir, matched_image):
                success_count += 1
            
            print()  # 空行分隔
        
        # 8. 完成報告
        print("═" * 50)
        print(f"✅ 處理完成！")
        print(f"📊 成功：{success_count}/{len(mp3_files)} 個檔案")
        print(f"📂 輸出位置：{output_dir}")
        print("═" * 50)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 使用者中斷操作")
    except Exception as e:
        print(f"\n❌ 程式執行錯誤：{e}")
    finally:
        input("\n按 Enter 鍵結束...")


if __name__ == "__main__":
    main()
