#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT字幕校正程序
使用原文来校正SRT字幕中的错误文字
"""

import re
import difflib
from typing import List, Tuple, Dict


class SRTCorrector:
    def __init__(self):
        # 常见的语音识别错误映射
        self.common_errors = {
            # 基本错字
            "罪苦": "最苦",
            "比秋": "比丘",
            "朱惠": "諸位",
            "此秋": "比丘",
            "頂利": "頂禮",
            "並告": "稟告",
            "開是": "開示",
            "爭議": "真義",
            "色深": "色身",
            "假深": "假身",
            "即可": "飢渴",
            "撐會": "瞋恚",
            "經部": "驚怖",
            "色域": "色欲",
            "遠禍": "怨禍",
            "重苦": "眾苦",
            "或患": "禍患",
            "遠胸": "元凶",
            "老心": "勞心",
            "優惠": "憂畏",
            "虛之": "須知",
            "重生": "眾生",
            "若若": "弱肉",
            "深死": "生死",
            # 佛教术语错误
            "釋迦摩尼": "釋迦牟尼",
            "阿羅漢": "阿羅漢",
            "舍衛國": "舍衛國",
            "祇洹": "祇洹",
            "精舍": "精舍",
            "他心通": "他心通",
            "宿命通": "宿命通",
            "天眼通": "天眼通",
            "天耳通": "天耳通",
            "神足通": "神足通",
            "涅槃": "涅槃",
            "輪迴": "輪迴",
            "六道": "六道",
            "三界": "三界",
            "煩惱": "煩惱",
            "寂滅": "寂滅",
        }

    def parse_srt(self, srt_content: str) -> List[Dict]:
        """解析SRT文件内容"""
        entries = []
        blocks = re.split(r"\n\s*\n", srt_content.strip())

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                # 序号
                sequence = int(lines[0])

                # 时间码
                timecode = lines[1]

                # 字幕文本（可能多行）
                text = " ".join(lines[2:])

                entries.append(
                    {"sequence": sequence, "timecode": timecode, "text": text}
                )

        return entries

    def extract_time_parts(self, timecode: str) -> Tuple[str, str]:
        """提取开始和结束时间"""
        start, end = timecode.split(" --> ")
        return start.strip(), end.strip()

    def correct_text(
        self, text: str, reference_text: str = None
    ) -> Tuple[str, List[str]]:
        """校正文本"""
        original_text = text
        corrections = []

        # 1. 使用错误映射表进行基本校正
        for wrong, correct in self.common_errors.items():
            if wrong in text:
                text = text.replace(wrong, correct)
                corrections.append(f"'{wrong}' → '{correct}'")

        # 2. 如果提供了参考文本，进行更精确的校正
        if reference_text:
            # 使用序列匹配找到最相似的部分
            matcher = difflib.SequenceMatcher(None, text, reference_text)
            similarity = matcher.ratio()

            if similarity < 0.8:  # 相似度低于80%时进行进一步分析
                # 找到最匹配的部分
                matches = matcher.get_matching_blocks()
                if matches:
                    # 提取可能的正确文本片段
                    for match in matches:
                        if match.size > 5:  # 只考虑较长的匹配
                            ref_part = reference_text[match.b : match.b + match.size]
                            text_part = text[match.a : match.a + match.size]
                            if ref_part != text_part:
                                corrections.append(
                                    f"片段校正: '{text_part}' → '{ref_part}'"
                                )

        # 3. 标点符号校正
        text = self.correct_punctuation(text)

        return text, corrections

    def correct_punctuation(self, text: str) -> str:
        """校正标点符号"""
        # 统一标点符号
        text = re.sub(r"[，、]", "，", text)
        text = re.sub(r"[。！？]{2,}", "。", text)
        text = re.sub(r"\s+", "", text)  # 移除多余空格

        return text

    def find_best_match_in_reference(
        self, srt_text: str, reference_text: str, min_length: int = 10
    ) -> str:
        """在参考文本中找到最佳匹配"""
        # 清理文本
        clean_srt = re.sub(r"[，。！？；：\s]", "", srt_text)
        clean_ref = re.sub(r"[，。！？；：\s]", "", reference_text)

        # 如果SRT文本太短，直接返回
        if len(clean_srt) < min_length:
            return srt_text

        # 在参考文本中搜索最相似的片段
        best_match = ""
        best_ratio = 0

        # 滑动窗口搜索
        window_size = len(clean_srt)
        for i in range(len(clean_ref) - window_size + 1):
            window = clean_ref[i : i + window_size]
            ratio = difflib.SequenceMatcher(None, clean_srt, window).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                # 从参考文本中提取对应的带标点版本
                start_pos = reference_text.find(window[:10])  # 找到开始位置
                if start_pos != -1:
                    # 尝试提取完整的句子或短语
                    end_pos = start_pos + len(srt_text)
                    if end_pos <= len(reference_text):
                        best_match = reference_text[start_pos:end_pos]

        return best_match if best_ratio > 0.7 else srt_text

    def correct_srt(
        self, srt_content: str, reference_text: str = None
    ) -> Tuple[str, List[str]]:
        """校正整个SRT文件"""
        entries = self.parse_srt(srt_content)
        corrected_entries = []
        all_corrections = []

        for entry in entries:
            original_text = entry["text"]

            # 校正文本
            if reference_text:
                # 先尝试在参考文本中找到最佳匹配
                best_match = self.find_best_match_in_reference(
                    original_text, reference_text
                )
                corrected_text, corrections = self.correct_text(
                    original_text, best_match
                )
            else:
                corrected_text, corrections = self.correct_text(original_text)

            # 记录修正信息
            if corrections:
                all_corrections.append(
                    f"第{entry['sequence']}段: {', '.join(corrections)}"
                )

            # 创建校正后的条目
            corrected_entries.append(
                {
                    "sequence": entry["sequence"],
                    "timecode": entry["timecode"],
                    "text": corrected_text,
                    "original_text": original_text,
                }
            )

        # 生成校正后的SRT内容
        corrected_srt = self.generate_srt(corrected_entries)

        return corrected_srt, all_corrections

    def generate_srt(self, entries: List[Dict]) -> str:
        """生成SRT格式文本"""
        srt_lines = []

        for entry in entries:
            srt_lines.append(str(entry["sequence"]))
            srt_lines.append(entry["timecode"])
            srt_lines.append(entry["text"])
            srt_lines.append("")  # 空行分隔

        return "\n".join(srt_lines)

    def generate_correction_report(
        self, corrections: List[str], original_srt: str, corrected_srt: str
    ) -> str:
        """生成校正报告"""
        report = []
        report.append("=" * 60)
        report.append("SRT字幕校正报告")
        report.append("=" * 60)
        report.append("")

        if corrections:
            report.append("🔧 发现的错误和修正：")
            for i, correction in enumerate(corrections, 1):
                report.append(f"  {i}. {correction}")
            report.append("")
        else:
            report.append("✅ 未发现需要修正的错误")
            report.append("")

        # 统计信息
        original_entries = len(self.parse_srt(original_srt))
        report.append(f"📊 统计信息：")
        report.append(f"  字幕条目数: {original_entries}")
        report.append(f"  修正项目数: {len(corrections)}")
        report.append("")

        report.append("=" * 60)
        return "\n".join(report)


def main():
    """主函数"""
    # 您的原文
    reference_text = """何事最苦:過去釋迦牟尼佛，在舍衛國祇洹精舍時，有一天四比丘，坐在樹下，互相討論：「世間所有一切，何事最苦？」甲比丘說：「天下最苦，就是淫欲。」乙比丘接看說：「世間瞋恨最苦。」丙比丘不以為然說：「淫欲、瞋恨，比不過飢渴的痛苦。」丁比丘搖頭說：「你們說的都比不上驚怖的痛苦。」四比丘各執己見，爭論不休。佛有他心通、宿命通，觀察四比丘得度機緣已到，於是來到四比丘前問說：「諸位比丘，正在討論何事？」四比丘向佛頂禮後，稟告剛才所爭論的問題。佛開示說：「你們都不知苦的根本真義，天下諸苦，皆由於有色身，有了假身，就有飢渴、寒熱、瞋恚、驚怖、色欲、怨禍等外苦，所以假身是眾苦的根本，禍患的元凶。至於內苦，更是勞心憂畏，苦惱萬端。須知三界眾生，無不弱肉強食，互相殘殺，因此在六道中，生死輪迴，受苦無窮，皆是由於有假身所致，若無假身，苦從何來？若想離苦，須求寂滅（不生不滅，萬緣寂靜），收攝妄心，不起妄念，正念相繼，淡泊守道，便可證得涅槃寂靜的境界，這才是真正最樂。」"""

    # 您的SRT内容
    srt_content = """1
00:00:00,000 --> 00:00:01,640
何事罪苦?

2
00:00:30,000 --> 00:00:44,480
佛有他心通,宿命通,觀察四比秋的度基源已到,於是來到四比秋前問說,朱惠此秋,正在討論何事,四比秋向佛頂利後,並告剛才所爭論的問題。

3
00:00:44,480 --> 00:00:59,700
佛開是說,你們都不知苦的根本爭議,天下諸苦,皆由於有色深,有了假深,就有即可,寒熱,撐會,經部,色域,遠禍等外苦,所以假深是重苦的根本,

4
00:00:59,700 --> 00:01:05,859
或患的遠胸。至於內苦,更是老心優惠苦腦萬端。

5
00:01:05,859 --> 00:01:18,900
虛之三界重生,無不若若強食,互相殘殺,因此在六道中,深死輪迴,受苦無窮,皆是由於有假深所致,若無假深苦從何來。"""

    # 创建校正器
    corrector = SRTCorrector()

    # 执行校正
    print("正在校正SRT字幕...")
    corrected_srt, corrections = corrector.correct_srt(srt_content, reference_text)

    # 生成报告
    report = corrector.generate_correction_report(
        corrections, srt_content, corrected_srt
    )

    # 显示结果
    print(report)
    print("\n校正后的SRT内容：")
    print("=" * 60)
    print(corrected_srt)

    # 保存文件
    with open("corrected_subtitle.srt", "w", encoding="utf-8") as f:
        f.write(corrected_srt)

    with open("correction_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
        f.write("\n\n原始SRT内容：\n")
        f.write("=" * 40 + "\n")
        f.write(srt_content)
        f.write("\n\n校正后SRT内容：\n")
        f.write("=" * 40 + "\n")
        f.write(corrected_srt)

    print(f"\n📁 文件已保存：")
    print(f"  - corrected_subtitle.srt (校正后的字幕)")
    print(f"  - correction_report.txt (详细校正报告)")


if __name__ == "__main__":
    main()
