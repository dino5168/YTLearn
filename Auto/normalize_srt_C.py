import re
from typing import List


class SubtitleEntry:
    def __init__(self, index: int, start: str, end: str, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text


def time_to_ms(t: str) -> int:
    # t 例如 "00:00:01,680"
    parts = t.split(":")
    s_part, ms = parts[2].split(",")
    h = int(parts[0])
    m = int(parts[1])
    s = int(s_part)
    ms = int(ms)
    return h * 3600000 + m * 60000 + s * 1000 + ms


def ms_to_time(ms: int) -> str:
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    ms = ms % 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def parse_srt(path: str) -> List[SubtitleEntry]:
    with open(path, encoding="utf-8") as f:
        blocks = re.split(r"\n{2,}", f.read().strip())

    entries = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            index = int(lines[0])
            start, end = re.split(r"\s-->\s", lines[1])
            text = " ".join(lines[2:]).strip()
            entries.append(SubtitleEntry(index, start, end, text))
    return entries


def calculate_sentence_weight(sentence: str) -> float:
    """
    計算句子權重，考慮中文字符、英文單詞數量和標點符號
    """
    # 中文字符權重較高
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", sentence))
    # 英文單詞
    english_words = len(re.findall(r"[a-zA-Z]+", sentence))
    # 標點符號權重較低
    punctuation = len(re.findall(r"[.!?,:;]", sentence))

    # 權重計算：中文字符*2 + 英文單詞*1.5 + 標點*0.5
    weight = chinese_chars * 2 + english_words * 1.5 + punctuation * 0.5
    return max(weight, 1)  # 最小權重為1


def merge_and_split_sentences(
    subs: List[SubtitleEntry],
    min_duration: int = 800,  # 最小持續時間(毫秒)
    max_duration: int = 6000,  # 最大持續時間(毫秒)
    time_adjustment: float = 0.0,
) -> List[SubtitleEntry]:
    """
    合併並分割句子，加入時間調整參數

    Args:
        subs: 字幕條目列表
        min_duration: 單句最小持續時間(毫秒)
        max_duration: 單句最大持續時間(毫秒)
        time_adjustment: 整體時間調整(秒)，正數延後，負數提前
    """
    merged = []
    buffer = []
    start_time = None
    index = 1

    # 時間調整轉換為毫秒
    time_offset = int(time_adjustment * 1000)

    for sub in subs:
        if not buffer:
            start_time = sub.start
        buffer.append(sub)

        if sub.text.strip().endswith((".", "!", "?")):
            full_text = " ".join(s.text for s in buffer)
            start_ms = time_to_ms(start_time) + time_offset
            end_ms = time_to_ms(sub.end) + time_offset
            total_duration = end_ms - start_ms

            sentences = re.split(r"(?<=[.!?])\s+", full_text.strip())

            # 使用改進的權重計算
            weights = [calculate_sentence_weight(s) for s in sentences]
            total_weight = sum(weights)
            ratios = [w / total_weight for w in weights]

            # 計算每句時長，並確保最小/最大限制
            durations = []
            remaining_duration = total_duration

            for i, ratio in enumerate(ratios):
                if i == len(ratios) - 1:  # 最後一句
                    duration = remaining_duration
                else:
                    duration = int(total_duration * ratio)
                    # 應用最小/最大時長限制
                    duration = max(min_duration, min(duration, max_duration))
                    remaining_duration -= duration

                durations.append(duration)

            # 確保最後一句至少有最小時長
            if durations[-1] < min_duration and len(durations) > 1:
                # 從前面的句子借用時間
                needed = min_duration - durations[-1]
                for i in range(len(durations) - 2, -1, -1):
                    if durations[i] > min_duration + needed:
                        durations[i] -= needed
                        durations[-1] += needed
                        break

            current_start = start_ms
            for s, d in zip(sentences, durations):
                current_end = current_start + d
                merged.append(
                    SubtitleEntry(
                        index=index,
                        start=ms_to_time(max(0, current_start)),  # 確保不會是負數
                        end=ms_to_time(max(0, current_end)),
                        text=s.strip(),
                    )
                )
                index += 1
                current_start = current_end

            buffer = []

    return merged


def adjust_timing_globally(
    subs: List[SubtitleEntry], offset_seconds: float
) -> List[SubtitleEntry]:
    """
    全域調整所有字幕的時間軸

    Args:
        subs: 字幕條目列表
        offset_seconds: 時間偏移(秒)，正數延後，負數提前
    """
    offset_ms = int(offset_seconds * 1000)

    adjusted = []
    for sub in subs:
        start_ms = time_to_ms(sub.start) + offset_ms
        end_ms = time_to_ms(sub.end) + offset_ms

        # 確保時間不會是負數
        start_ms = max(0, start_ms)
        end_ms = max(0, end_ms)

        adjusted.append(
            SubtitleEntry(
                index=sub.index,
                start=ms_to_time(start_ms),
                end=ms_to_time(end_ms),
                text=sub.text,
            )
        )

    return adjusted


def write_srt(subs: List[SubtitleEntry], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for sub in subs:
            f.write(f"{sub.index}\n")
            f.write(f"{sub.start} --> {sub.end}\n")
            f.write(f"{sub.text.strip()}\n\n")


def validate_timing(subs: List[SubtitleEntry]) -> List[str]:
    """
    驗證時間軸是否有問題並返回警告訊息
    """
    warnings = []

    for i, sub in enumerate(subs):
        start_ms = time_to_ms(sub.start)
        end_ms = time_to_ms(sub.end)
        duration = end_ms - start_ms

        # 檢查持續時間是否過短
        if duration < 500:
            warnings.append(
                f"第 {sub.index} 句持續時間過短 ({duration}ms): {sub.text[:20]}..."
            )

        # 檢查持續時間是否過長
        if duration > 8000:
            warnings.append(
                f"第 {sub.index} 句持續時間過長 ({duration}ms): {sub.text[:20]}..."
            )

        # 檢查是否與下一句重疊
        if i < len(subs) - 1:
            next_start = time_to_ms(subs[i + 1].start)
            if end_ms > next_start:
                warnings.append(f"第 {sub.index} 句與第 {subs[i + 1].index} 句時間重疊")

    return warnings


if __name__ == "__main__":
    input_path = "c:/temp/c.srt"
    output_path = "c:/temp/normalized.srt"

    # 可調整的參數
    MIN_DURATION = 800  # 最小持續時間(毫秒)
    MAX_DURATION = 6000  # 最大持續時間(毫秒)
    TIME_ADJUSTMENT = 0.0  # 整體時間調整(秒)，可設定如 -0.5 或 +1.2
    GLOBAL_OFFSET = 0.0  # 全域時間偏移(秒)

    parsed = parse_srt(input_path)
    print(f"📖 讀取了 {len(parsed)} 個字幕條目")

    # 正規化處理
    normalized = merge_and_split_sentences(
        parsed,
        min_duration=MIN_DURATION,
        max_duration=MAX_DURATION,
        time_adjustment=TIME_ADJUSTMENT,
    )
    print(f"🔄 正規化後共 {len(normalized)} 個句子")

    # 如果需要全域時間調整
    if GLOBAL_OFFSET != 0:
        normalized = adjust_timing_globally(normalized, GLOBAL_OFFSET)
        print(f"⏰ 已調整整體時間軸 {GLOBAL_OFFSET} 秒")

    # 驗證時間軸
    warnings = validate_timing(normalized)
    if warnings:
        print("⚠️  時間軸警告:")
        for warning in warnings[:5]:  # 只顯示前5個警告
            print(f"   {warning}")
        if len(warnings) > 5:
            print(f"   ... 還有 {len(warnings) - 5} 個警告")

    write_srt(normalized, output_path)
    print(f"✅ 字幕正規化完成！輸出檔案：{output_path}")

    # 顯示調整建議
    print("\n💡 如果時間軸還有誤差，可以調整以下參數:")
    print("   - TIME_ADJUSTMENT: 製作過程中的時間微調")
    print("   - GLOBAL_OFFSET: 整體字幕時間偏移")
    print("   - MIN_DURATION/MAX_DURATION: 單句最小/最大持續時間")
