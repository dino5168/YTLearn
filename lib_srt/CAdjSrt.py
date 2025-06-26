import re
from datetime import datetime
from typing import List, Dict
import aiofiles


# 調整字幕檔使用,有的字幕時間軸的資料會不一致需要調整
class CAdjSrt:
    TIME_FORMAT = "%H:%M:%S,%f"

    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.blocks: List[Dict] = []

    @classmethod
    def parse_time(cls, t: str) -> datetime:
        return datetime.strptime(t, cls.TIME_FORMAT)

    @classmethod
    def format_time(cls, t: datetime) -> str:
        return t.strftime(cls.TIME_FORMAT)[:-3]  # 保留到毫秒

    async def read_srt(self):
        async with aiofiles.open(self.input_path, "r", encoding="utf-8") as f:
            content = await f.read()

        blocks_raw = re.split(r"\n\s*\n", content.strip())
        self.blocks = []

        for block in blocks_raw:
            lines = block.strip().splitlines()
            if len(lines) < 3:
                continue
            idx = lines[0].strip()
            times = lines[1].strip()
            en = lines[2].strip()
            zh = lines[3].strip() if len(lines) > 3 else ""

            m = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", times
            )
            if not m:
                continue

            start = self.parse_time(m.group(1))
            end = self.parse_time(m.group(2))

            self.blocks.append(
                {"idx": idx, "start": start, "end": end, "en": en, "zh": zh}
            )

    def adjust_end_times(self):
        for i in range(len(self.blocks) - 1):
            self.blocks[i]["end"] = self.blocks[i + 1]["start"]

    async def write_srt(self):
        async with aiofiles.open(self.output_path, "w", encoding="utf-8") as f:
            for b in self.blocks:
                await f.write(f"{b['idx']}\n")
                await f.write(
                    f"{self.format_time(b['start'])} --> {self.format_time(b['end'])}\n"
                )
                await f.write(f"{b['en']}\n")
                if b["zh"]:
                    await f.write(f"{b['zh']}\n")
                await f.write("\n")

    async def process(self):
        await self.read_srt()
        self.adjust_end_times()
        await self.write_srt()
