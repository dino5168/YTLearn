import asyncio
import edge_tts
import os
import re
from pydub import AudioSegment
import tempfile


def parse_srt(file_path):
    """解析 SRT 檔案，回傳 [(序號, 開始秒數, 結束秒數, 文字)] 的列表"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 根據 SRT 檔格式分段
    pattern = r"(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3})\s-->\s(\d{2}:\d{2}:\d{2},\d{3})\s+(.*?)(?=\n\n|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    result = []
    for index, start, end, text in matches:
        # 清除行內換行
        clean_text = text.replace("\n", " ").strip()
        # 轉換時間格式為秒數
        start_seconds = time_to_seconds(start)
        end_seconds = time_to_seconds(end)
        result.append((int(index), start_seconds, end_seconds, clean_text))

    return result


def time_to_seconds(time_str):
    """將 SRT 時間格式 (HH:MM:SS,mmm) 轉換為秒數"""
    time_part, ms_part = time_str.split(",")
    hours, minutes, seconds = map(int, time_part.split(":"))
    milliseconds = int(ms_part)

    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    return total_seconds


def seconds_to_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


async def generate_speech_segment(text, voice, temp_file):
    """生成單個語音片段"""
    try:
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(temp_file)
        return True
    except Exception as e:
        print(f"❌ 語音生成失敗: {e}")
        return False


async def srt_to_synced_speech(
    srt_path,
    voice="zh-TW-HsiaoChenNeural",
    output_file="synced_audio.mp3",
    method="stretch",  # "stretch" 或 "gap"
):
    """
    將 SRT 轉換為時間同步的語音檔案
    method:
    - "stretch": 拉伸/壓縮音檔以符合時間軸
    - "gap": 保持原始語音速度，用靜音填補間隙
    """
    if not os.path.exists(srt_path):
        print(f"❌ 找不到 SRT 檔案：{srt_path}")
        return

    segments = parse_srt(srt_path)
    if not segments:
        print("⚠️ 未解析到任何字幕段落")
        return

    print(f"🎤 開始轉換，共 {len(segments)} 段字幕...")
    print(f"📊 方法：{'時間拉伸' if method == 'stretch' else '靜音填補'}")

    # 計算總時長
    total_duration = max(end for _, _, end, _ in segments)
    print(f"⏱️ 總時長：{seconds_to_time(total_duration)}")

    # 創建空白音檔作為基底
    final_audio = AudioSegment.silent(duration=int(total_duration * 1000))

    with tempfile.TemporaryDirectory() as temp_dir:
        for index, start_time, end_time, text in segments:
            if not text.strip():
                continue

            print(
                f"➡️ [{index:04d}] {seconds_to_time(start_time)} --> {seconds_to_time(end_time)}: {text[:30]}..."
            )

            # 生成語音檔案
            temp_file = os.path.join(temp_dir, f"temp_{index}.mp3")
            success = await generate_speech_segment(text, voice, temp_file)

            if not success:
                continue

            try:
                # 載入生成的音檔
                speech_audio = AudioSegment.from_mp3(temp_file)
                target_duration = (end_time - start_time) * 1000  # 轉為毫秒

                if method == "stretch":
                    # 方法1: 拉伸/壓縮音檔以符合時間軸
                    if len(speech_audio) != target_duration:
                        # 計算播放速度倍率
                        speed_ratio = len(speech_audio) / target_duration
                        if speed_ratio > 0.5 and speed_ratio < 2.0:  # 合理的速度範圍
                            # 調整音檔長度
                            speech_audio = speech_audio._spawn(
                                speech_audio.raw_data,
                                overrides={
                                    "frame_rate": int(
                                        speech_audio.frame_rate * speed_ratio
                                    )
                                },
                            ).set_frame_rate(speech_audio.frame_rate)
                        else:
                            # 如果速度差異太大，裁切或填補
                            if len(speech_audio) > target_duration:
                                speech_audio = speech_audio[: int(target_duration)]
                            else:
                                speech_audio = speech_audio + AudioSegment.silent(
                                    duration=int(target_duration - len(speech_audio))
                                )

                elif method == "gap":
                    # 方法2: 保持原始語音速度，用靜音填補
                    if len(speech_audio) > target_duration:
                        # 如果語音太長，裁切
                        speech_audio = speech_audio[: int(target_duration)]
                    elif len(speech_audio) < target_duration:
                        # 如果語音太短，後面加靜音
                        silence_duration = target_duration - len(speech_audio)
                        speech_audio = speech_audio + AudioSegment.silent(
                            duration=int(silence_duration)
                        )

                # 將音檔插入到正確的時間位置
                start_ms = int(start_time * 1000)
                end_ms = int(end_time * 1000)

                # 確保不超出範圍
                if start_ms < len(final_audio) and end_ms <= len(final_audio):
                    # 覆蓋到最終音檔上
                    final_audio = (
                        final_audio[:start_ms]
                        + speech_audio[: end_ms - start_ms]
                        + final_audio[end_ms:]
                    )

            except Exception as e:
                print(f"❌ 第 {index} 段處理失敗: {e}")

    # 輸出最終音檔
    try:
        final_audio.export(output_file, format="mp3")
        print(f"\n✅ 轉換完成！輸出檔案：{output_file}")
        print(f"📁 檔案大小：{os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
    except Exception as e:
        print(f"❌ 輸出失敗: {e}")


async def srt_to_individual_segments(
    srt_path, voice="zh-TW-HsiaoChenNeural", output_dir="timed_segments"
):
    """生成個別的時間同步音檔片段"""
    if not os.path.exists(srt_path):
        print(f"❌ 找不到 SRT 檔案：{srt_path}")
        return

    segments = parse_srt(srt_path)
    if not segments:
        print("⚠️ 未解析到任何字幕段落")
        return

    # 建立輸出資料夾
    os.makedirs(output_dir, exist_ok=True)

    print(f"🎤 開始轉換個別片段，共 {len(segments)} 段字幕...")

    for index, start_time, end_time, text in segments:
        if not text.strip():
            continue

        duration = end_time - start_time
        filename = os.path.join(
            output_dir,
            f"{index:04d}_{seconds_to_time(start_time).replace(':', '-').replace(',', '-')}_duration-{duration:.1f}s.mp3",
        )

        print(
            f"➡️ [{index:04d}] {seconds_to_time(start_time)} --> {seconds_to_time(end_time)} ({duration:.1f}s): {text[:30]}..."
        )

        try:
            communicate = edge_tts.Communicate(text, voice=voice)
            await communicate.save(filename)
        except Exception as e:
            print(f"❌ 第 {index} 段轉換失敗: {e}")

    print(f"\n✅ 所有片段轉換完成！輸出資料夾：{output_dir}")


def main():
    srt_path = input("請輸入 SRT 字幕檔路徑: ").strip()

    print("\n請選擇語音：")
    voices = {
        "1": ("zh-TW-HsiaoChenNeural", "台灣女生 - 小陳"),
        "2": ("zh-TW-YunJheNeural", "台灣男生 - 雲哲"),
        "3": ("zh-CN-XiaoxiaoNeural", "大陸女生 - 曉曉"),
        "4": ("zh-CN-YunxiNeural", "大陸男生 - 雲希"),
        "5": ("en-US-JennyNeural", "英語女生 - Jenny"),
        "6": ("en-US-GuyNeural", "英語男生 - Guy"),
    }

    for key, (_, desc) in voices.items():
        print(f"{key}. {desc}")
    voice_choice = input("請選擇語音 (1-6): ").strip()
    voice = voices.get(voice_choice, voices["1"])[0]

    print("\n請選擇輸出模式：")
    print("1. 合併為單一同步音檔 (時間拉伸)")
    print("2. 合併為單一同步音檔 (靜音填補)")
    print("3. 個別片段檔案 (含時間資訊)")
    mode = input("請選擇模式 (1-3): ").strip()

    try:
        if mode == "1":
            output_file = (
                input("輸出檔名 (預設: synced_audio_stretch.mp3): ").strip()
                or "synced_audio_stretch.mp3"
            )
            asyncio.run(srt_to_synced_speech(srt_path, voice, output_file, "stretch"))
        elif mode == "2":
            output_file = (
                input("輸出檔名 (預設: synced_audio_gap.mp3): ").strip()
                or "synced_audio_gap.mp3"
            )
            asyncio.run(srt_to_synced_speech(srt_path, voice, output_file, "gap"))
        elif mode == "3":
            output_dir = (
                input("輸出資料夾 (預設: timed_segments): ").strip() or "timed_segments"
            )
            asyncio.run(srt_to_individual_segments(srt_path, voice, output_dir))
        else:
            print("❌ 無效的選擇")
            return

    except KeyboardInterrupt:
        print("\n程式已中斷。")
    except Exception as e:
        print(f"執行失敗: {e}")


if __name__ == "__main__":
    main()
