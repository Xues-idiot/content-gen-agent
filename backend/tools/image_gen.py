"""
Vox Image Generator 模块

负责图片生成和素材推荐
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

import requests
from loguru import logger

from backend.config import config


class ImageStyle(Enum):
    """图片风格"""
    MODERN = "modern"
    MINIMAL = "minimal"
    LIFESTYLE = "lifestyle"
    PRODUCT = "product"
    COMPARISON = "comparison"


@dataclass
class ImageResult:
    """图片结果"""
    url: str = ""
    prompt: str = ""
    style: str = ""
    success: bool = True
    error: str = ""


@dataclass
class ImageSuggestion:
    """图片建议"""
    type: str  # 产品图、场景图、对比图等
    description: str
    prompt: str  # 用于生成的 prompt
    style: ImageStyle = ImageStyle.MODERN


class ImageGenerator:
    """
    图片生成 Agent

    支持：
    - DALL-E/MJ API 生成
    - 素材库推荐
    """

    def __init__(self):
        self.openai_api_key = config.minimax_api_key
        self.openai_base_url = config.minimax_base_url

    def generate_image(
        self,
        prompt: str,
        style: str = "modern",
        size: str = "1024x1024",
    ) -> ImageResult:
        """
        使用 DALL-E 生成图片

        Args:
            prompt: 图片描述
            style: 风格
            size: 图片尺寸

        Returns:
            ImageResult: 生成结果
        """
        logger.info(f"Generating image with prompt: {prompt[:50]}...")

        # 注意：这里需要 OpenAI 兼容的 API
        # MiniMax 可能需要不同的实现
        try:
            # 预留接口，实际使用时需要根据 API 调整
            return ImageResult(
                url=f"https://placeholder.com/image?prompt={prompt[:50]}",
                prompt=prompt,
                style=style,
            )
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return ImageResult(success=False, error=str(e))

    def suggest_images(
        self,
        product_name: str,
        product_category: str,
        platform: str = "xiaohongshu",
    ) -> List[ImageSuggestion]:
        """
        根据产品和平台推荐图片类型

        Args:
            product_name: 产品名称
            product_category: 产品类别
            platform: 目标平台

        Returns:
            List[ImageSuggestion]: 图片建议列表
        """
        suggestions = []

        if platform == "xiaohongshu":
            suggestions = [
                ImageSuggestion(
                    type="产品图",
                    description="清晰的产品主图，展示产品全貌",
                    prompt=f"{product_name} 产品主图，白色背景，现代简洁风格",
                    style=ImageStyle.PRODUCT,
                ),
                ImageSuggestion(
                    type="场景图",
                    description="产品在实际使用场景中的照片",
                    prompt=f"{product_name} 在温馨家居场景中，高生活质量",
                    style=ImageStyle.LIFESTYLE,
                ),
                ImageSuggestion(
                    type="对比图",
                    description="使用前后对比或产品对比",
                    prompt=f"{product_name} 使用效果对比，专业摄影",
                    style=ImageStyle.COMPARISON,
                ),
                ImageSuggestion(
                    type="细节图",
                    description="产品细节特写",
                    prompt=f"{product_name} 细节特写，高质感",
                    style=ImageStyle.MINIMAL,
                ),
            ]
        elif platform == "tiktok":
            suggestions = [
                ImageSuggestion(
                    type="短视频封面",
                    description="吸引眼球的视频封面图",
                    prompt=f"{product_name} 视频封面，大字标题，视觉冲击",
                    style=ImageStyle.MODERN,
                ),
                ImageSuggestion(
                    type="产品展示",
                    description="适合短视频的产品展示图",
                    prompt=f"{product_name} 产品展示，动态感",
                    style=ImageStyle.LIFESTYLE,
                ),
            ]
        elif platform == "official":
            suggestions = [
                ImageSuggestion(
                    type="文章配图",
                    description="与文章内容相关的配图",
                    prompt=f"{product_name} 相关配图，专业编辑风格",
                    style=ImageStyle.MINIMAL,
                ),
                ImageSuggestion(
                    type="产品详情图",
                    description="详细展示产品特点和细节",
                    prompt=f"{product_name} 详细展示，信息丰富",
                    style=ImageStyle.PRODUCT,
                ),
            ]
        elif platform == "friend_circle":
            suggestions = [
                ImageSuggestion(
                    type="朋友圈配图",
                    description="适合朋友圈分享的产品图",
                    prompt=f"{product_name} 朋友圈分享图，生活化",
                    style=ImageStyle.LIFESTYLE,
                ),
            ]

        return suggestions

    def search_stock_images(
        self,
        keyword: str,
        count: int = 5,
    ) -> List[str]:
        """
        从素材库搜索图片（预留接口）

        Args:
            keyword: 搜索关键词
            count: 返回数量

        Returns:
            List[str]: 图片 URL 列表
        """
        # 预留接口，实际可以对接 Pexels、Unsplash 等
        logger.info(f"Searching stock images for: {keyword}")
        return [f"https://placeholder.com/stock/{keyword}_{i}.jpg" for i in range(count)]


if __name__ == "__main__":
    generator = ImageGenerator()

    # 测试建议
    suggestions = generator.suggest_images("智能睡眠枕", "家居", "xiaohongshu")
    for s in suggestions:
        print(f"{s.type}: {s.description}")
