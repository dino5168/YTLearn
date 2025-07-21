from faster_whisper import WhisperModel
import torch


class FasterWhisperTranscriber:

    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        """
        初始化 FasterWhisper 模型。
        :param model_size: 模型大小，例如 "small", "medium", "large-v3"
        :param device: "cuda" or "cpu"，若為 None 則自動偵測
        :param compute_type: "int8", "float16", etc.
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[FasterWhisper] 初始化模型 {model_size} on {self.device}")
        self.model = WhisperModel(
            model_size, device=self.device, compute_type=compute_type
        )

    def transcribe_to_srt(self, input_path: str, output_srt_path: str):
        """
        將語音檔轉錄並輸出為 SRT 字幕檔
        :param input_path: 音訊檔路徑 (.mp3, .wav, .mp4)
        :param output_srt_path: SRT 字幕輸出路徑
        """
        print(f"[FasterWhisper] 開始轉錄：{input_path}")
        segments, info = self.model.transcribe(input_path, beam_size=5)
        print(f"[FasterWhisper] 偵測語言：{info.language}")

        def format_timestamp(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        with open(output_srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                f.write(f"{i}\n")
                f.write(
                    f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n"
                )
                print(f"{segment.text.strip()}\n\n")
                f.write(f"{segment.text.strip()}\n\n")

        print(f"[FasterWhisper] 已輸出字幕：{output_srt_path}")
