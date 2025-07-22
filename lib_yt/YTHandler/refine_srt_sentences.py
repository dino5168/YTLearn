import re
import nltk
from datetime import timedelta

nltk.download("punkt_tab")


def srt_time_to_seconds(srt_time: str) -> float:
    h, m, s_ms = srt_time.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def seconds_to_srt_time(seconds: float) -> str:
    # 修正：直接处理秒数，不使用timedelta
    total_seconds = int(seconds)
    ms = int((seconds - total_seconds) * 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def parse_srt(srt_text: str):
    pattern = re.compile(
        r"(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.*?)(?=\n\d+\s+\d{2}:\d{2}:\d{2},\d{3}|\Z)",
        re.DOTALL,
    )
    entries = []
    for match in pattern.finditer(srt_text):
        index, start, end, text = match.groups()
        entries.append(
            {
                "start": srt_time_to_seconds(start),
                "end": srt_time_to_seconds(end),
                "text": text.replace("\n", " ").strip(),
            }
        )
    return entries


def split_and_rescale(segments):
    new_entries = []
    counter = 1
    for seg in segments:
        sentences = nltk.sent_tokenize(seg["text"])
        if not sentences:
            continue

        total_chars = sum(len(s) for s in sentences)
        start_time = seg["start"]
        end_time = seg["end"]
        total_duration = end_time - start_time

        time_cursor = start_time
        for sentence in sentences:
            proportion = len(sentence) / total_chars
            sentence_duration = total_duration * proportion
            sentence_start = time_cursor
            sentence_end = sentence_start + sentence_duration
            new_entries.append(
                {
                    "index": counter,
                    "start": seconds_to_srt_time(sentence_start),
                    "end": seconds_to_srt_time(sentence_end),
                    "text": sentence.strip(),
                }
            )
            time_cursor = sentence_end
            counter += 1
    return new_entries


def generate_srt(entries):
    srt_lines = []
    for entry in entries:
        srt_lines.append(f"{entry['index']}")
        srt_lines.append(f"{entry['start']} --> {entry['end']}")
        srt_lines.append(f"{entry['text']}")
        srt_lines.append("")
    return "\n".join(srt_lines)


def refine(input_file: str, output_file: str):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            srt_text = f.read()

        segments = parse_srt(srt_text)
        if not segments:
            print("❌ 无法解析SRT文件或文件为空")
            return

        refined = split_and_rescale(segments)
        output_srt = generate_srt(refined)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_srt)

        print(f"✅ 重新分割字幕已儲存到: {output_file}")
        print(f"📊 原始字幕段数: {len(segments)}, 分割后段数: {len(refined)}")

    except FileNotFoundError:
        print(f"❌ 找不到文件: {input_file}")
    except Exception as e:
        print(f"❌ 处理过程中出错: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # refine("input.srt", "output.srt")
    pass
