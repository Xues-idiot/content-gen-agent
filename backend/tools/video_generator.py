"""
Vox Video Generator 模块

基于 MoneyPrinterTurbo 的视频生成实现
负责视频素材处理、字幕生成、视频合成
"""

import glob
import itertools
import os
import random
import gc
import shutil
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

from loguru import logger


class VideoAspect(Enum):
    """视频比例"""
    PORTRAIT = "9:16"  # 竖屏 1080x1920
    LANDSCAPE = "16:9"  # 横屏 1920x1080
    SQUARE = "1:1"  # 方屏 1080x1080

    def to_resolution(self) -> Tuple[int, int]:
        """返回 (width, height)"""
        if self == VideoAspect.PORTRAIT:
            return (1080, 1920)
        elif self == VideoAspect.LANDSCAPE:
            return (1920, 1080)
        else:
            return (1080, 1080)


class VideoConcatMode(Enum):
    """视频拼接模式"""
    RANDOM = "random"
    SEQUENTIAL = "sequential"


class VideoTransitionMode(Enum):
    """视频转场模式"""
    NONE = "none"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    SHUFFLE = "shuffle"


@dataclass
class VideoParams:
    """视频生成参数"""
    video_aspect: VideoAspect = VideoAspect.PORTRAIT
    video_concat_mode: VideoConcatMode = VideoConcatMode.RANDOM
    video_transition_mode: VideoTransitionMode = VideoTransitionMode.FADE_IN
    video_clip_duration: int = 5  # 每个片段最大时长
    n_threads: int = 2
    # 字幕参数
    subtitle_enabled: bool = True
    font_name: str = "STHeitiMedium.ttc"
    font_size: int = 60
    text_fore_color: str = "white"
    text_background_color: str = "transparent"
    stroke_color: str = "black"
    stroke_width: float = 1.0
    subtitle_position: str = "bottom"  # bottom/top/center/custom
    custom_position: float = 50.0  # 自定义位置百分比
    # 背景音乐参数
    bgm_type: str = "random"  # random/none
    bgm_file: str = ""
    bgm_volume: float = 0.3
    # 语音参数
    voice_name: str = "zh-CN-XiaoyiNeural"
    voice_rate: float = 1.0
    voice_volume: float = 1.0
    # 视频数量
    video_count: int = 1


@dataclass
class VideoResult:
    """视频生成结果"""
    video_path: str = ""
    audio_path: str = ""
    subtitle_path: str = ""
    duration: float = 0.0
    success: bool = True
    error: str = ""


@dataclass
class MaterialInfo:
    """素材信息"""
    provider: str = ""  # pexels/pixabay/local
    url: str = ""
    duration: float = 0.0
    width: int = 0
    height: int = 0


class VideoGenerator:
    """
    视频生成器

    基于 MoneyPrinterTurbo 架构，支持:
    - Pexels/Pixabay 视频素材搜索
    - TTS 语音合成
    - 字幕生成
    - 视频拼接与合成
    """

    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "output", "videos")
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_bgm_file(self, bgm_type: str = "random", bgm_file: str = "") -> str:
        """获取背景音乐文件"""
        if not bgm_type or bgm_type == "none":
            return ""

        if bgm_file and os.path.exists(bgm_file):
            return bgm_file

        if bgm_type == "random":
            # 优先从本地 resource/songs 获取
            song_dirs = [
                os.path.join(os.getcwd(), "resource", "songs"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "_reference", "resource", "songs"),
            ]
            for song_dir in song_dirs:
                if os.path.exists(song_dir):
                    files = glob.glob(os.path.join(song_dir, "*.mp3"))
                    if files:
                        return random.choice(files)

        return ""

    def _wrap_text(self, text: str, max_width: float, font: str = "Arial", fontsize: int = 60) -> Tuple[str, int]:
        """文本自动换行"""
        try:
            from PIL import ImageFont
            image_font = ImageFont.truetype(font, fontsize)

            def get_text_size(inner_text: str) -> Tuple[int, int]:
                inner_text = inner_text.strip()
                left, top, right, bottom = image_font.getbbox(inner_text)
                return right - left, bottom - top

            width, height = get_text_size(text)
            if width <= max_width:
                return text, height

            wrapped_lines = []
            current_line = ""
            words = text.split(" ")

            for word in words:
                before = current_line
                current_line += f"{word} "
                w, h = get_text_size(current_line)
                if w <= max_width:
                    continue
                else:
                    if current_line.strip() == word.strip():
                        break
                    wrapped_lines.append(before)
                    current_line = f"{word} "

            wrapped_lines.append(current_line)
            result = "\n".join([line.strip() for line in wrapped_lines if line.strip()])
            return result, len(wrapped_lines) * height

        except Exception as e:
            logger.warning(f"Text wrapping failed, using original text: {e}")
            return text, 30

    def _close_clip(self, clip) -> None:
        """安全关闭 clip 资源"""
        if clip is None:
            return

        try:
            if hasattr(clip, 'reader') and clip.reader is not None:
                clip.reader.close()

            if hasattr(clip, 'audio') and clip.audio is not None:
                if hasattr(clip.audio, 'reader') and clip.audio.reader is not None:
                    clip.audio.reader.close()
                del clip.audio

            if hasattr(clip, 'mask') and clip.mask is not None:
                if hasattr(clip.mask, 'reader') and clip.mask.reader is not None:
                    clip.mask.reader.close()
                del clip.mask

            if hasattr(clip, 'clips') and clip.clips:
                for child_clip in clip.clips:
                    if child_clip is not clip:
                        self._close_clip(child_clip)

            if hasattr(clip, 'clips'):
                clip.clips = []

        except Exception as e:
            logger.error(f"Failed to close clip: {str(e)}")

        del clip
        gc.collect()

    def _delete_files(self, files: List[str]) -> None:
        """删除文件列表"""
        if isinstance(files, str):
            files = [files]

        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception:
                pass

    def combine_videos(
        self,
        video_paths: List[str],
        audio_path: str,
        output_path: str,
        params: VideoParams
    ) -> str:
        """
        拼接多个视频为一个视频

        Args:
            video_paths: 视频文件路径列表
            audio_path: 音频文件路径
            output_path: 输出路径
            params: 视频参数

        Returns:
            拼接后的视频路径
        """
        try:
            from moviepy import (
                AudioFileClip,
                ColorClip,
                CompositeVideoClip,
                ImageClip,
                VideoFileClip,
                concatenate_videoclips,
            )

            if not video_paths:
                logger.warning("No videos to combine")
                return ""

            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            video_width, video_height = params.video_aspect.to_resolution()

            # 每个片段的最大时长
            max_clip_duration = params.video_clip_duration

            subclipped_items = []
            for video_path in video_paths:
                try:
                    clip = VideoFileClip(video_path)
                    clip_duration = clip.duration
                    clip_w, clip_h = clip.size
                    self._close_clip(clip)

                    start_time = 0
                    while start_time < clip_duration:
                        end_time = min(start_time + max_clip_duration, clip_duration)
                        subclipped_items.append({
                            "path": video_path,
                            "start": start_time,
                            "end": end_time,
                            "width": clip_w,
                            "height": clip_h
                        })
                        start_time = end_time

                        if params.video_concat_mode == VideoConcatMode.SEQUENTIAL:
                            break

                except Exception as e:
                    logger.error(f"Failed to process video {video_path}: {e}")

            # 随机打乱顺序
            if params.video_concat_mode == VideoConcatMode.RANDOM:
                random.shuffle(subclipped_items)

            # 处理每个片段
            processed_clips = []
            video_duration = 0.0
            output_dir = os.path.dirname(output_path) or "."

            for i, item in enumerate(subclipped_items):
                if video_duration > audio_duration:
                    break

                try:
                    clip = VideoFileClip(item["path"]).subclipped(item["start"], item["end"])
                    clip_duration = clip.duration

                    # 调整尺寸
                    clip_w, clip_h = clip.size
                    if clip_w != video_width or clip_h != video_height:
                        clip_ratio = clip_w / clip_h
                        video_ratio = video_width / video_height

                        if clip_ratio == video_ratio:
                            clip = clip.resized(new_size=(video_width, video_height))
                        else:
                            if clip_ratio > video_ratio:
                                scale_factor = video_width / clip_w
                            else:
                                scale_factor = video_height / clip_h

                            new_width = int(clip_w * scale_factor)
                            new_height = int(clip_h * scale_factor)

                            background = ColorClip(size=(video_width, video_height), color=(0, 0, 0)).with_duration(clip_duration)
                            clip_resized = clip.resized(new_size=(new_width, new_height)).with_position("center")
                            clip = CompositeVideoClip([background, clip_resized])

                    # 转场效果
                    transition = params.video_transition_mode
                    if transition == VideoTransitionMode.FADE_IN:
                        clip = clip.fadein(1.0)
                    elif transition == VideoTransitionMode.FADE_OUT:
                        clip = clip.fadeout(1.0)

                    if clip.duration > max_clip_duration:
                        clip = clip.subclipped(0, max_clip_duration)

                    # 写入临时文件
                    clip_file = f"{output_dir}/temp-clip-{i+1}.mp4"
                    clip.write_videofile(clip_file, logger=None, fps=30, codec="libx264")
                    self._close_clip(clip)

                    processed_clips.append({
                        "path": clip_file,
                        "duration": clip.duration
                    })
                    video_duration += clip.duration

                except Exception as e:
                    logger.error(f"Failed to process clip {i+1}: {e}")

            # 循环填充直到音频结束
            if video_duration < audio_duration and processed_clips:
                base_clips = processed_clips.copy()
                for clip in itertools.cycle(base_clips):
                    if video_duration >= audio_duration:
                        break
                    processed_clips.append(clip)
                    video_duration += clip["duration"]

            # 合并视频
            if len(processed_clips) == 1:
                shutil.copy(processed_clips[0]["path"], output_path)
                self._delete_files([c["path"] for c in processed_clips])
                return output_path

            # 逐步合并
            temp_merged = f"{output_dir}/temp-merged.mp4"
            shutil.copy(processed_clips[0]["path"], temp_merged)

            for i, clip_info in enumerate(processed_clips[1:], 1):
                try:
                    base_clip = VideoFileClip(temp_merged)
                    next_clip = VideoFileClip(clip_info["path"])
                    merged = concatenate_videoclips([base_clip, next_clip])

                    temp_next = f"{output_dir}/temp-merged-next.mp4"
                    merged.write_videofile(
                        temp_next,
                        threads=params.n_threads,
                        logger=None,
                        temp_audiofile_path=output_dir,
                        fps=30,
                    )

                    self._close_clip(base_clip)
                    self._close_clip(next_clip)
                    self._close_clip(merged)

                    self._delete_files(temp_merged)
                    os.rename(temp_next, temp_merged)

                except Exception as e:
                    logger.error(f"Failed to merge clip {i}: {e}")

            os.rename(temp_merged, output_path)
            self._delete_files([c["path"] for c in processed_clips])

            logger.success(f"Video combined: {output_path}")
            return output_path

        except ImportError as e:
            logger.error(f"MoviePy not installed: {e}")
            return ""
        except Exception as e:
            logger.error(f"Failed to combine videos: {e}")
            return ""

    def generate_video(
        self,
        video_path: str,
        audio_path: str,
        subtitle_path: str,
        output_path: str,
        params: VideoParams
    ) -> VideoResult:
        """
        生成最终视频（添加字幕和音频）

        Args:
            video_path: 视频路径
            audio_path: 音频路径
            subtitle_path: 字幕路径
            output_path: 输出路径
            params: 视频参数

        Returns:
            VideoResult
        """
        try:
            from moviepy import (
                AudioFileClip,
                CompositeAudioClip,
                CompositeVideoClip,
                TextClip,
                VideoFileClip,
                afx,
            )
            from moviepy.video.tools.subtitles import SubtitlesClip

            video_width, video_height = params.video_aspect.to_resolution()
            logger.info(f"Generating video: {video_width}x{video_height}")

            # 获取字体路径
            font_path = ""
            if params.subtitle_enabled:
                font_dir = os.path.join(os.getcwd(), "resource", "fonts")
                if os.path.exists(font_dir):
                    font_path = os.path.join(font_dir, params.font_name)
                    if not os.path.exists(font_path):
                        font_path = ""

            def create_text_clip(subtitle_item) -> 'TextClip':
                """创建字幕片段"""
                phrase = subtitle_item[1]
                max_width = video_width * 0.9

                wrapped_txt, txt_height = self._wrap_text(
                    phrase,
                    max_width=max_width,
                    font=font_path,
                    fontsize=params.font_size
                )

                clip = TextClip(
                    text=wrapped_txt,
                    font=font_path,
                    font_size=params.font_size,
                    color=params.text_fore_color,
                    bg_color=params.text_background_color if params.text_background_color != "transparent" else None,
                    stroke_color=params.stroke_color,
                    stroke_width=params.stroke_width,
                )

                start_time = subtitle_item[0][0]
                end_time = subtitle_item[0][1]
                duration = end_time - start_time

                clip = clip.with_start(start_time)
                clip = clip.with_end(end_time)
                clip = clip.with_duration(duration)

                # 位置
                if params.subtitle_position == "bottom":
                    clip = clip.with_position(("center", video_height * 0.95 - clip.h))
                elif params.subtitle_position == "top":
                    clip = clip.with_position(("center", video_height * 0.05))
                elif params.subtitle_position == "center":
                    clip = clip.with_position(("center", "center"))
                else:
                    custom_y = (video_height - clip.h) * (params.custom_position / 100)
                    clip = clip.with_position(("center", custom_y))

                return clip

            # 加载视频和音频
            video_clip = VideoFileClip(video_path).without_audio()
            audio_clip = AudioFileClip(audio_path).with_effects(
                [afx.MultiplyVolume(params.voice_volume)]
            )

            def make_textclip(text: str) -> 'TextClip':
                return TextClip(
                    text=text,
                    font=font_path,
                    font_size=params.font_size,
                )

            # 添加字幕
            if subtitle_path and os.path.exists(subtitle_path):
                try:
                    sub = SubtitlesClip(subtitles=subtitle_path, encoding="utf-8", make_textclip=make_textclip)
                    text_clips = [create_text_clip(item) for item in sub.subtitles]
                    video_clip = CompositeVideoClip([video_clip, *text_clips])
                except Exception as e:
                    logger.warning(f"Failed to add subtitles: {e}")

            # 添加背景音乐
            bgm_file = self._get_bgm_file(params.bgm_type, params.bgm_file)
            if bgm_file:
                try:
                    bgm_clip = AudioFileClip(bgm_file).with_effects(
                        [
                            afx.MultiplyVolume(params.bgm_volume),
                            afx.AudioFadeOut(3),
                            afx.AudioLoop(duration=video_clip.duration),
                        ]
                    )
                    audio_clip = CompositeAudioClip([audio_clip, bgm_clip])
                except Exception as e:
                    logger.warning(f"Failed to add BGM: {e}")

            # 添加音频
            video_clip = video_clip.with_audio(audio_clip)

            # 输出视频
            output_dir = os.path.dirname(output_path) or "."
            video_clip.write_videofile(
                output_path,
                audio_codec="aac",
                temp_audiofile_path=output_dir,
                threads=params.n_threads or 2,
                logger=None,
                fps=30,
            )

            self._close_clip(video_clip)

            logger.success(f"Video generated: {output_path}")

            return VideoResult(
                video_path=output_path,
                audio_path=audio_path,
                subtitle_path=subtitle_path,
                duration=audio_clip.duration,
                success=True
            )

        except ImportError as e:
            logger.error(f"MoviePy not installed: {e}")
            return VideoResult(success=False, error=f"Missing dependency: {e}")
        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            return VideoResult(success=False, error=str(e))

    def preprocess_video_materials(
        self,
        materials: List[MaterialInfo],
        clip_duration: int = 4
    ) -> List[MaterialInfo]:
        """
        预处理视频素材（将图片转换为视频片段）

        Args:
            materials: 素材列表
            clip_duration: 片段时长

        Returns:
            处理后的素材列表
        """
        try:
            from moviepy import ImageClip, VideoFileClip, CompositeVideoClip
        except ImportError:
            logger.warning("MoviePy not installed, skipping preprocessing")
            return materials

        for material in materials:
            if not material.url:
                continue

            ext = os.path.splitext(material.url)[-1].lower()
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']

            if ext in image_extensions:
                logger.info(f"Processing image: {material.url}")

                try:
                    # 创建图片片段并添加缩放效果
                    clip = (
                        ImageClip(material.url)
                        .with_duration(clip_duration)
                        .with_position("center")
                    )

                    # 添加缩放动画效果
                    zoom_clip = clip.resized(
                        lambda t: 1 + (clip_duration * 0.03) * (t / clip_duration)
                    )

                    final_clip = CompositeVideoClip([zoom_clip])
                    video_file = f"{material.url}.mp4"
                    final_clip.write_videofile(video_file, fps=30, logger=None)

                    self._close_clip(clip)
                    self._close_clip(final_clip)

                    material.url = video_file
                    logger.success(f"Image processed: {video_file}")

                except Exception as e:
                    logger.warning(f"Failed to process image {material.url}: {e}")

        return materials


# 全局实例
video_generator = VideoGenerator()


if __name__ == "__main__":
    # 测试代码
    generator = VideoGenerator()

    params = VideoParams(
        video_aspect=VideoAspect.PORTRAIT,
        subtitle_enabled=True,
        font_size=48,
    )

    print("VideoGenerator initialized")
    print(f"Output directory: {generator.output_dir}")
