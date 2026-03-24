"""
Vox Material Collector 模块

负责视频素材搜索和下载
支持 Pexels、Pixabay 视频素材源
"""

import os
import random
import hashlib
from typing import List
from urllib.parse import urlencode

from loguru import logger

from backend.config import config


class MaterialCollector:
    """
    素材收集器

    支持：
    - Pexels 视频搜索
    - Pixabay 视频搜索
    - 本地素材目录
    """

    def __init__(self):
        self.cache_dir = os.path.join(os.getcwd(), "cache", "videos")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_api_key(self, cfg_key: str) -> str:
        """获取 API key"""
        api_keys = config.app.get(cfg_key, [])
        if isinstance(api_keys, str):
            return api_keys
        if isinstance(api_keys, list) and api_keys:
            return random.choice(api_keys)
        return ""

    def _md5(self, text: str) -> str:
        """计算 MD5 哈希"""
        return hashlib.md5(text.encode()).hexdigest()

    def _ensure_dir(self, directory: str) -> str:
        """确保目录存在"""
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def search_videos_pexels(
        self,
        search_term: str,
        video_aspect: str = "9:16",
        per_page: int = 15,
    ) -> List[dict]:
        """
        从 Pexels 搜索视频素材

        Args:
            search_term: 搜索关键词
            video_aspect: 视频比例 (9:16, 16:9, 1:1)
            per_page: 返回数量

        Returns:
            视频素材列表
        """
        api_key = self._get_api_key("pexels_api_keys")
        if not api_key:
            logger.warning("Pexels API key not configured")
            return []

        # Pexels API 支持的 orientation: portrait, landscape, square
        orientation_map = {
            "9:16": "portrait",
            "16:9": "landscape",
            "1:1": "square",
        }
        orientation = orientation_map.get(video_aspect, "portrait")

        headers = {
            "Authorization": api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        params = {
            "query": search_term,
            "per_page": per_page,
            "orientation": orientation,
        }

        url = f"https://api.pexels.com/videos/search?{urlencode(params)}"

        try:
            import requests
            response = requests.get(
                url,
                headers=headers,
                timeout=(30, 60),
            )
            response.raise_for_status()
            data = response.json()

            videos = []
            for item in data.get("videos", []):
                duration = item.get("duration", 0)
                if duration < 3:  # 跳过太短的素材
                    continue

                # 找到最佳分辨率的视频文件
                video_files = item.get("video_files", [])
                best_video = None
                for vf in video_files:
                    w = vf.get("width", 0)
                    h = vf.get("height", 0)
                    # 优先匹配目标分辨率
                    if video_aspect == "9:16" and h >= 1920:
                        best_video = vf
                        break
                    elif video_aspect == "16:9" and w >= 1920:
                        best_video = vf
                        break
                    elif video_aspect == "1:1" and w >= 1080:
                        best_video = vf
                        break

                if not best_video and video_files:
                    best_video = video_files[0]

                if best_video:
                    videos.append({
                        "provider": "pexels",
                        "url": best_video.get("link", ""),
                        "duration": duration,
                        "width": best_video.get("width", 0),
                        "height": best_video.get("height", 0),
                        "id": item.get("id", ""),
                    })

            logger.info(f"Pexels search: '{search_term}' -> {len(videos)} videos")
            return videos

        except ImportError:
            logger.warning("requests library not available")
            return []
        except Exception as e:
            logger.error(f"Pexels search failed: {e}")
            return []

    def search_videos_pixabay(
        self,
        search_term: str,
        video_aspect: str = "9:16",
        per_page: int = 20,
    ) -> List[dict]:
        """
        从 Pixabay 搜索视频素材

        Args:
            search_term: 搜索关键词
            video_aspect: 视频比例
            per_page: 返回数量

        Returns:
            视频素材列表
        """
        api_key = self._get_api_key("pixabay_api_keys")
        if not api_key:
            logger.warning("Pixabay API key not configured")
            return []

        params = {
            "q": search_term,
            "video_type": "all",
            "per_page": per_page,
            "key": api_key,
        }

        url = f"https://pixabay.com/api/videos/?{urlencode(params)}"

        try:
            import requests
            response = requests.get(
                url,
                timeout=(30, 60),
            )
            response.raise_for_status()
            data = response.json()

            videos = []
            for item in data.get("hits", []):
                duration = item.get("duration", 0)
                if duration < 3:
                    continue

                # 优先匹配目标分辨率
                video_sizes = item.get("videos", {})
                size_priority = ["fullhd", "hd", "sd"]

                best_video = None
                target_width = 1920 if video_aspect == "16:9" else (1080 if video_aspect == "1:1" else 1080)

                for size in size_priority:
                    if size in video_sizes:
                        vf = video_sizes[size]
                        if vf.get("width", 0) >= target_width:
                            best_video = vf
                            break

                if not best_video and video_sizes:
                    for vf in video_sizes.values():
                        if not best_video:
                            best_video = vf
                        elif vf.get("width", 0) > best_video.get("width", 0):
                            best_video = vf

                if best_video:
                    videos.append({
                        "provider": "pixabay",
                        "url": best_video.get("url", ""),
                        "duration": duration,
                        "width": best_video.get("width", 0),
                        "height": best_video.get("height", 0),
                        "id": item.get("id", ""),
                    })

            logger.info(f"Pixabay search: '{search_term}' -> {len(videos)} videos")
            return videos

        except ImportError:
            logger.warning("requests library not available")
            return []
        except Exception as e:
            logger.error(f"Pixabay search failed: {e}")
            return []

    def search_videos(
        self,
        search_term: str,
        video_aspect: str = "9:16",
        source: str = "pexels",
    ) -> List[dict]:
        """
        搜索视频素材（统一接口）

        Args:
            search_term: 搜索关键词
            video_aspect: 视频比例
            source: 素材源 (pexels/pixabay)

        Returns:
            视频素材列表
        """
        if source == "pixabay":
            return self.search_videos_pixabay(search_term, video_aspect)
        return self.search_videos_pexels(search_term, video_aspect)

    def _get_video_path(self, video_url: str, save_dir: str = "") -> str:
        """生成视频保存路径"""
        if not save_dir:
            save_dir = self.cache_dir

        url_hash = self._md5(video_url.split("?")[0])
        filename = f"vid-{url_hash}.mp4"
        return os.path.join(save_dir, filename)

    def download_video(
        self,
        video_url: str,
        save_dir: str = "",
    ) -> str:
        """
        下载单个视频

        Args:
            video_url: 视频 URL
            save_dir: 保存目录

        Returns:
            视频本地路径，失败返回空字符串
        """
        save_dir = save_dir or self.cache_dir
        self._ensure_dir(save_dir)

        video_path = self._get_video_path(video_url, save_dir)

        # 如果已存在，直接返回
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            logger.info(f"Video already exists: {video_path}")
            return video_path

        try:
            import requests

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(
                video_url,
                headers=headers,
                timeout=(60, 240),
                stream=True,
            )
            response.raise_for_status()

            with open(video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # 验证下载的视频是否有效
            from moviepy.video.io.VideoFileClip import VideoFileClip
            clip = VideoFileClip(video_path)
            if clip.duration > 0:
                clip.close()
                logger.info(f"Video downloaded: {video_path}")
                return video_path
            clip.close()

        except ImportError:
            logger.warning("requests or moviepy not available")
        except Exception as e:
            logger.error(f"Failed to download video: {e}")

        # 下载失败，清理文件
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception:
                pass

        return ""

    def download_videos(
        self,
        search_terms: List[str],
        video_aspect: str = "9:16",
        source: str = "pexels",
        audio_duration: float = 60.0,
        max_clip_duration: int = 5,
    ) -> List[str]:
        """
        批量下载视频素材

        Args:
            search_terms: 搜索关键词列表
            video_aspect: 视频比例
            source: 素材源
            audio_duration: 目标音频时长
            max_clip_duration: 最大片段时长

        Returns:
            下载的视频路径列表
        """
        all_videos = []
        seen_urls = set()

        for term in search_terms:
            videos = self.search_videos(term, video_aspect, source)
            for video in videos:
                if video["url"] not in seen_urls:
                    all_videos.append(video)
                    seen_urls.add(video["url"])

        # 随机打乱顺序
        random.shuffle(all_videos)

        video_paths = []
        total_duration = 0.0

        for video in all_videos:
            if total_duration >= audio_duration:
                break

            logger.info(f"Downloading video: {video['url']}")
            path = self.download_video(video["url"])
            if path:
                video_paths.append(path)
                total_duration += min(video["duration"], max_clip_duration)

        logger.success(f"Downloaded {len(video_paths)} videos, total duration: {total_duration:.1f}s")
        return video_paths


# 全局实例
material_collector = MaterialCollector()


if __name__ == "__main__":
    collector = MaterialCollector()

    # 测试搜索
    videos = collector.search_videos("nature", "9:16", "pexels")
    print(f"Found {len(videos)} videos")

    # 测试下载
    if videos:
        path = collector.download_video(videos[0]["url"])
        print(f"Downloaded to: {path}")