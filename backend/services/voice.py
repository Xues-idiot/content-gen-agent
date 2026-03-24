"""
Vox Voice Service 模块

语音合成服务
支持 Edge TTS (微软，免费)
"""

import asyncio
import os
import re
from typing import List, Optional, Tuple, Dict, Any

from loguru import logger

from backend.config import config


class VoiceService:
    """
    语音合成服务

    支持：
    - Edge TTS (微软，免费，推荐)
    """

    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "output", "audio")
        os.makedirs(self.output_dir, exist_ok=True)

    def _format_rate(self, rate: float) -> str:
        """将速率转换为 Edge TTS 格式"""
        if rate == 1.0:
            return "+0%"
        percent = round((rate - 1.0) * 100)
        if percent > 0:
            return f"+{percent}%"
        return f"{percent}%"

    def _split_text(self, text: str) -> List[str]:
        """按标点符号分割文本"""
        # 简单实现，按句号、问号、感叹号分割
        pattern = r'[^。？！.!?。\n]+[。？！.!?。\n]?'
        matches = re.findall(pattern, text.strip())
        return [m.strip() for m in matches if m.strip()]

    def generate_audio(
        self,
        text: str,
        voice_name: str = "zh-CN-XiaoyiNeural",
        voice_rate: float = 1.0,
        output_path: str = "",
    ) -> Tuple[str, float]:
        """
        使用 Edge TTS 生成语音

        Args:
            text: 要转换的文本
            voice_name: 声音名称
            voice_rate: 语速 (0.5-2.0)
            output_path: 输出文件路径

        Returns:
            (音频文件路径, 时长)
        """
        if not output_path:
            import uuid
            filename = f"tts-{uuid.uuid4().hex[:8]}.mp3"
            output_path = os.path.join(self.output_dir, filename)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        rate_str = self._format_rate(voice_rate)
        sub_maker = None

        try:
            import edge_tts

            async def _do() -> Tuple:
                nonlocal sub_maker
                communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
                sub_maker = edge_tts.SubMaker()

                with open(output_path, "wb") as file:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            file.write(chunk["data"])
                        elif chunk["type"] == "WordBoundary":
                            sub_maker.create_sub(
                                (chunk["offset"], chunk["duration"]),
                                chunk["text"]
                            )

                return output_path

            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已经在运行中，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _do())
                    result = future.result()
            else:
                result = asyncio.run(_do())

            # 获取音频时长
            audio_duration = self._get_duration(output_path)
            logger.success(f"TTS generated: {output_path}, duration: {audio_duration:.2f}s")

            return output_path, audio_duration

        except ImportError:
            logger.error("edge-tts not installed. Install with: pip install edge-tts")
            return "", 0.0
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return "", 0.0

    def _get_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        try:
            from moviepy import AudioFileClip
            clip = AudioFileClip(audio_path)
            duration = clip.duration
            clip.close()
            return duration
        except Exception:
            return 0.0

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        获取可用的声音列表

        Returns:
            声音列表，每项包含 name, language, gender
        """
        # Edge TTS 支持的声音列表（常用中文）
        voices = [
            # 中文女声
            {"name": "zh-CN-XiaoxiaoNeural", "language": "zh-CN", "gender": "Female"},
            {"name": "zh-CN-XiaoyiNeural", "language": "zh-CN", "gender": "Female"},
            {"name": "zh-CN-YunxiNeural", "language": "zh-CN", "gender": "Male"},
            {"name": "zh-CN-YunyangNeural", "language": "zh-CN", "gender": "Male"},
            {"name": "zh-CN-liaoning-XiaobeiNeural", "language": "zh-CN-LN", "gender": "Female"},
            {"name": "zh-CN-shaanxi-XiaoniNeural", "language": "zh-CN-SX", "gender": "Female"},
            # 中文男声
            {"name": "zh-CN-YunjianNeural", "language": "zh-CN", "gender": "Male"},
            # 粤语
            {"name": "zh-HK-HiuGaaiNeural", "language": "zh-HK", "gender": "Female"},
            {"name": "zh-HK-WanLungNeural", "language": "zh-HK", "gender": "Male"},
            # 台湾话
            {"name": "zh-TW-HsiaoChenNeural", "language": "zh-TW", "gender": "Female"},
            {"name": "zh-TW-YunJheNeural", "language": "zh-TW", "gender": "Male"},
        ]
        return voices

    def generate_with_subtitles(
        self,
        text: str,
        voice_name: str = "zh-CN-XiaoyiNeural",
        voice_rate: float = 1.0,
        output_dir: str = "",
    ) -> Tuple[str, str, float]:
        """
        生成音频并创建字幕文件

        Args:
            text: 要转换的文本
            voice_name: 声音名称
            voice_rate: 语速
            output_dir: 输出目录

        Returns:
            (音频路径, 字幕路径, 时长)
        """
        if not output_dir:
            output_dir = self.output_dir

        os.makedirs(output_dir, exist_ok=True)

        import uuid
        audio_path = os.path.join(output_dir, f"audio-{uuid.uuid4().hex[:8]}.mp3")
        subtitle_path = os.path.join(output_dir, f"audio-{uuid.uuid4().hex[:8]}.srt")

        audio_path, duration = self.generate_audio(
            text=text,
            voice_name=voice_name,
            voice_rate=voice_rate,
            output_path=audio_path,
        )

        if not audio_path:
            return "", "", 0.0

        # 生成字幕
        self._create_subtitle(
            text=text,
            audio_duration=duration,
            subtitle_path=subtitle_path,
        )

        return audio_path, subtitle_path, duration

    def _create_subtitle(
        self,
        text: str,
        audio_duration: float,
        subtitle_path: str,
    ) -> bool:
        """创建字幕文件"""
        try:
            sentences = self._split_text(text)
            if not sentences:
                return False

            total_chars = sum(len(s) for s in sentences)
            if total_chars == 0:
                return False

            char_duration = audio_duration / total_chars
            current_time = 0.0

            lines = []
            for i, sentence in enumerate(sentences, 1):
                start_time = current_time
                end_time = start_time + len(sentence) * char_duration

                lines.append(self._format_srt_line(
                    i,
                    start_time,
                    end_time,
                    sentence
                ))

                current_time = end_time

            with open(subtitle_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

            logger.info(f"Subtitle created: {subtitle_path}")
            return True

        except Exception as e:
            logger.error(f"Subtitle creation failed: {e}")
            return False

    def _format_srt_line(
        self,
        index: int,
        start_time: float,
        end_time: float,
        text: str,
    ) -> str:
        """格式化 SRT 时间线"""
        def time_to_srt(t: float) -> str:
            hours = int(t // 3600)
            minutes = int((t % 3600) // 60)
            seconds = int(t % 60)
            millis = int((t % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

        start = time_to_srt(start_time)
        end = time_to_srt(end_time)
        return f"{index}\n{start} --> {end}\n{text}"


# 全局实例
voice_service = VoiceService()


if __name__ == "__main__":
    service = VoiceService()

    # 获取可用声音
    voices = service.get_available_voices()
    print(f"Available voices: {len(voices)}")

    # 测试 TTS
    text = "这是一段测试文本，用于验证语音合成功能是否正常工作。"
    audio_path, duration = service.generate_audio(text)
    print(f"Audio: {audio_path}, Duration: {duration:.2f}s")