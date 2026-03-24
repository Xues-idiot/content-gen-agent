"""
Vox Subtitle Service 模块

字幕生成服务
支持 Whisper 语音识别生成字幕
"""

import os
import re
from typing import List, Optional, Tuple, Dict, Any

from loguru import logger


class SubtitleService:
    """
    字幕生成服务

    支持：
    - Whisper 语音识别生成字幕
    - 字幕文件校正
    """

    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "output", "subtitles")
        os.makedirs(self.output_dir, exist_ok=True)
        self._model = None

    def _get_model(self):
        """获取 Whisper 模型（延迟加载）"""
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel

            model_size = "large-v3"
            device = "cpu"
            compute_type = "int8"

            logger.info(f"Loading Whisper model: {model_size}")

            self._model = WhisperModel(
                model_size_or_path=model_size,
                device=device,
                compute_type=compute_type,
            )

            logger.success("Whisper model loaded")
            return self._model

        except ImportError:
            logger.warning("faster-whisper not installed. Install with: pip install faster-whisper")
            return None
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return None

    def generate_subtitle(
        self,
        audio_path: str,
        output_path: str = "",
        language: str = "zh",
    ) -> str:
        """
        使用 Whisper 生成字幕

        Args:
            audio_path: 音频文件路径
            output_path: 输出字幕路径
            language: 语音语言

        Returns:
            字幕文件路径
        """
        if not output_path:
            import uuid
            filename = f"subtitle-{uuid.uuid4().hex[:8]}.srt"
            output_path = os.path.join(self.output_dir, filename)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        model = self._get_model()
        if model is None:
            logger.warning("Whisper model not available, skipping subtitle generation")
            return ""

        try:
            logger.info(f"Generating subtitle for: {audio_path}")

            segments, info = model.transcribe(
                audio_path,
                beam_size=5,
                word_timestamps=True,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                language=language if language != "auto" else None,
            )

            logger.info(f"Detected language: {info.language}, probability: {info.language_probability:.2f}")

            subtitles = []

            def add_subtitle(text: str, start: float, end: float):
                text = text.strip()
                if not text:
                    return
                subtitles.append({
                    "text": text,
                    "start": start,
                    "end": end,
                })

            for segment in segments:
                seg_text = ""
                seg_start = 0.0
                seg_end = 0.0

                if segment.words:
                    for i, word in enumerate(segment.words):
                        if i == 0:
                            seg_start = word.start
                        seg_end = word.end
                        seg_text += word.word

                        # 遇到标点符号分割
                        if self._is_punctuation(word.word):
                            seg_text = seg_text[:-1]
                            if seg_text.strip():
                                add_subtitle(seg_text, seg_start, seg_end)
                            seg_text = ""
                            seg_start = 0.0

                    # 处理剩余文本
                    if seg_text.strip():
                        add_subtitle(seg_text, seg_start, seg_end)

            # 写入 SRT 文件
            with open(output_path, "w", encoding="utf-8") as f:
                for i, sub in enumerate(subtitles, 1):
                    f.write(self._format_srt(i, sub["start"], sub["end"], sub["text"]) + "\n")

            logger.success(f"Subtitle generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Subtitle generation failed: {e}")
            return ""

    def _is_punctuation(self, char: str) -> bool:
        """判断是否是标点符号"""
        puncts = '，。？！、；：""''（）【】《》——…·.,?!;:""''()[]<>-'
        return char in puncts

    def _format_srt(
        self,
        index: int,
        start_time: float,
        end_time: float,
        text: str,
    ) -> str:
        """格式化 SRT 行"""
        def ts(t: float) -> str:
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        return f"{index}\n{ts(start_time)} --> {ts(end_time)}\n{text}"

    def correct_subtitle(
        self,
        subtitle_path: str,
        original_script: str,
    ) -> bool:
        """
        校正字幕文件

        使用原始脚本校正 Whisper 生成的字幕，
        处理识别错误和分割不准确的问题

        Args:
            subtitle_path: 字幕文件路径
            original_script: 原始脚本文本

        Returns:
            是否成功
        """
        if not os.path.exists(subtitle_path):
            logger.warning(f"Subtitle file not found: {subtitle_path}")
            return False

        try:
            # 读取字幕
            subtitle_items = self._parse_srt(subtitle_path)
            if not subtitle_items:
                return False

            # 按标点分割原始脚本
            script_lines = self._split_script(original_script)

            # 使用 Levenshtein 距离匹配和校正
            corrected = self._align_subtitles(subtitle_items, script_lines)

            if corrected:
                # 写回字幕文件
                with open(subtitle_path, "w", encoding="utf-8") as f:
                    for i, (idx, times, text) in enumerate(subtitle_items, 1):
                        f.write(f"{i}\n{times}\n{text}\n\n")
                logger.info("Subtitle corrected")
            else:
                logger.success("Subtitle is already correct")

            return True

        except Exception as e:
            logger.error(f"Subtitle correction failed: {e}")
            return False

    def _parse_srt(self, path: str) -> List[Tuple[int, str, str]]:
        """解析 SRT 文件"""
        items = []
        current_index = None
        current_times = None
        current_text = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    if current_index is not None:
                        items.append((
                            current_index,
                            current_times,
                            "".join(current_text).strip()
                        ))
                    current_index = None
                    current_times = None
                    current_text = []
                elif current_index is None:
                    try:
                        current_index = int(line)
                    except ValueError:
                        pass
                elif current_times is None:
                    current_times = line
                else:
                    current_text.append(line)

        return items

    def _split_script(self, script: str) -> List[str]:
        """按标点符号分割脚本"""
        pattern = r'[^，。？！、；：""''（）【】《》——…·.,?!;:""''()[\]<>!-]+[，。？！、；：""''（）【】《》——…·.,?!;:""''()[\]<>!-]?'
        matches = re.findall(pattern, script.strip())
        return [m.strip() for m in matches if m.strip()]

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                ins = prev_row[j + 1] + 1
                dele = curr_row[j] + 1
                subst = prev_row[j] + (c1 != c2)
                curr_row.append(min(ins, dele, subst))
            prev_row = curr_row

        return prev_row[-1]

    def _similarity(self, a: str, b: str) -> float:
        """计算相似度"""
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        dist = self._levenshtein_distance(a.lower(), b.lower())
        return 1 - (dist / max(len(a), len(b)))

    def _align_subtitles(
        self,
        subtitles: List[Tuple],
        script_lines: List[str],
    ) -> bool:
        """对齐字幕和脚本"""
        corrected = False
        new_subtitles = []
        script_idx = 0
        sub_idx = 0

        while script_idx < len(script_lines) and sub_idx < len(subtitles):
            script_line = script_lines[script_idx].strip()
            sub_text = subtitles[sub_idx][2].strip()

            if script_line == sub_text:
                new_subtitles.append(subtitles[sub_idx])
                script_idx += 1
                sub_idx += 1
            else:
                # 尝试合并相邻字幕
                combined = sub_text
                times = subtitles[sub_idx][1]
                next_idx = sub_idx + 1

                while next_idx < len(subtitles):
                    next_text = subtitles[next_idx][2].strip()
                    if self._similarity(script_line, combined + next_text) > self._similarity(script_line, combined):
                        combined += " " + next_text
                        times = subtitles[next_idx][1]
                        next_idx += 1
                    else:
                        break

                sim = self._similarity(script_line, combined)
                if sim > 0.8:
                    logger.warning(f"Corrected: '{sub_text}' -> '{script_line}'")
                    new_subtitles.append((len(new_subtitles) + 1, times, script_line))
                    corrected = True
                else:
                    logger.warning(f"Low similarity ({sim:.2f}): script='{script_line}', sub='{combined}'")
                    new_subtitles.append((len(new_subtitles) + 1, times, script_line))
                    corrected = True

                script_idx += 1
                sub_idx = next_idx

        # 处理剩余的脚本行
        while script_idx < len(script_lines):
            logger.warning(f"Extra script line: {script_lines[script_idx]}")
            new_subtitles.append((
                len(new_subtitles) + 1,
                "00:00:00,000 --> 00:00:00,000",
                script_lines[script_idx]
            ))
            script_idx += 1
            corrected = True

        if corrected:
            subtitles.clear()
            subtitles.extend(new_subtitles)

        return corrected

    def parse_srt(self, path: str) -> List[Dict[str, Any]]:
        """
        解析 SRT 文件并返回结构化数据

        Args:
            path: SRT 文件路径

        Returns:
            字幕列表，每项包含 start, end, text
        """
        items = self._parse_srt(path)
        result = []

        for _, times, text in items:
            try:
                start_str, end_str = times.split(" --> ")
                result.append({
                    "text": text,
                    "start": self._parse_time(start_str),
                    "end": self._parse_time(end_str),
                })
            except Exception:
                pass

        return result

    def _parse_time(self, time_str: str) -> float:
        """解析 SRT 时间字符串为秒数"""
        # 格式: 00:00:00,000
        match = re.match(r'(\d+):(\d+):(\d+),(\d+)', time_str)
        if match:
            h, m, s, ms = match.groups()
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        return 0.0


# 全局实例
subtitle_service = SubtitleService()


if __name__ == "__main__":
    service = SubtitleService()

    # 测试解析
    # subtitle_path = "test.srt"
    # items = service.parse_srt(subtitle_path)
    # print(f"Parsed {len(items)} subtitles")

    print("SubtitleService initialized")