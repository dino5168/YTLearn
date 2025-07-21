# transcriber.py
import torch
from faster_whisper import WhisperModel


class FasterWhisperTranscriber:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[FasterWhisper] 初始化模型 {model_size} on {self.device}")
        self.model = WhisperModel(
            model_size, device=self.device, compute_type=compute_type
        )

    def format_timestamp(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    def transcribe_to_srt(self, input_path: str, output_srt_path: str) -> dict:
        print(f"[FasterWhisper] 開始轉錄：{input_path}")
        segments, info = self.model.transcribe(input_path, beam_size=5)
        print(f"[FasterWhisper] 偵測語言：{info.language}")

        with open(output_srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                f.write(f"{i}\n")
                f.write(
                    f"{self.format_timestamp(segment.start)} --> {self.format_timestamp(segment.end)}\n"
                )
                f.write(f"{segment.text.strip()}\n\n")

        return {"srt_path": output_srt_path, "lan": info.language}
