# 使用文字產製 mp3 與字幕檔
import asyncio
import edge_tts
import re
from pathlib import Path
from pydub import AudioSegment


class StoryVoiceGenerator:
    def __init__(
        self,
        voice: str = "en-US-JennyNeural",
        output_dir: Path = Path("c:/temp/0715"),
        output_mp3: str = "note.mp3",
        output_srt: str = "note.srt",
        silence_ms: int = 300,
    ):
        self.voice = voice
        self.output_dir = output_dir
        self.output_mp3 = self.output_dir / output_mp3
        self.output_srt = self.output_dir / output_srt
        self.silence_ms = silence_ms

        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def split_text_into_sentences(text: str):
        pattern = r"(?<=[.!?])\s+"
        sentences = re.split(pattern, text.strip())
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def format_timestamp(ms: int) -> str:
        seconds, milliseconds = divmod(ms, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    async def generate_voice_file(self, text: str, index: int) -> Path:
        output_path = self.output_dir / f"{index:03d}.mp3"
        tts = edge_tts.Communicate(text, voice=self.voice)
        await tts.save(str(output_path))
        print(f"✔️ 產生語音: {output_path.name}")
        return output_path

    async def generate_story_from_text(self, content: str):
        # 切句
        sentences = self.split_text_into_sentences(content)
        print(f"📖 共 {len(sentences)} 句話")

        temp_files = []
        for idx, sentence in enumerate(sentences):
            path = await self.generate_voice_file(sentence, idx + 1)
            temp_files.append((path, sentence))

        # 合併 + 建立 SRT
        combined = AudioSegment.empty()
        srt_entries = []
        current_time = 0

        for idx, (path, text) in enumerate(temp_files):
            segment = AudioSegment.from_mp3(path)
            start = current_time
            end = current_time + len(segment)

            srt_entry = f"{idx + 1}\n{self.format_timestamp(start)} --> {self.format_timestamp(end)}\n{text}\n"
            srt_entries.append(srt_entry)

            combined += segment
            combined += AudioSegment.silent(duration=self.silence_ms)
            current_time = end + self.silence_ms

        combined.export(self.output_mp3, format="mp3")
        print(f"\n✅ 合併音檔輸出: {self.output_mp3.resolve()}")

        with open(self.output_srt, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_entries))
        print(f"✅ 字幕檔輸出: {self.output_srt.resolve()}")

    async def generate_story_from_text_file(self, text_file: str):
        with open(text_file, "r", encoding="utf-8") as f:
            content = f.read()
        await self.generate_story_from_text(content)
