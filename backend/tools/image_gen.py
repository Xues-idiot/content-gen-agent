"""
Vox Image Generator 模块

负责图片生成和素材推荐
支持 Pollinations AI (免费)、DALL-E、MJ 等
"""

import os
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

from loguru import logger

from backend.config import config


class ImageStyle(Enum):
    """图片风格"""
    MODERN = "modern"
    MINIMAL = "minimal"
    LIFESTYLE = "lifestyle"
    PRODUCT = "product"
    COMPARISON = "comparison"
    NATURAL = "natural"
    VIVID = "vivid"


@dataclass
class ImageResult:
    """图片结果"""
    url: str = ""
    local_path: str = ""
    prompt: str = ""
    style: str = ""
    width: int = 1024
    height: int = 1024
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
    - Pollinations AI (免费，推荐)
    - OpenAI DALL-E
    - 素材库推荐
    """

    # Pollinations 模型
    POLLINATIONS_MODELS = {
        "fast": "openai",
        "quality": "stable-diffusion",
    }

    # Pollinations 尺寸映射
    SIZE_MAP = {
        "square": (1024, 1024),
        "portrait": (896, 1152),
        "landscape": (1152, 896),
        "wide": (1280, 720),
    }

    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "output", "images")
        os.makedirs(self.output_dir, exist_ok=True)

    def _build_pollinations_url(
        self,
        prompt: str,
        model: str = "openai",
        width: int = 1024,
        height: int = 1024,
        seed: int = None,
    ) -> str:
        """构建 Pollinations URL"""
        # Pollinations 公共 API
        base_url = "https://image.pollinations.ai/prompt"

        # URL 编码 prompt
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)

        # 构建 URL 参数
        params = [
            f"prompt={encoded_prompt}",
            f"width={width}",
            f"height={height}",
            f"model={model}",
            "nologo=true",
        ]

        if seed:
            params.append(f"seed={seed}")

        return f"{base_url}?{'&'.join(params)}"

    def generate_image(
        self,
        prompt: str,
        style: str = "modern",
        size: str = "square",
        model: str = "openai",
    ) -> ImageResult:
        """
        使用 Pollinations AI 生成图片

        Args:
            prompt: 图片描述
            style: 风格 (modern/minimal/lifestyle/product/natural/vivid)
            size: 尺寸 (square/portrait/landscape/wide)
            model: 模型 (openai/stable-diffusion)

        Returns:
            ImageResult: 生成结果
        """
        logger.info(f"Generating image with Pollinations: {prompt[:50]}...")

        try:
            # 获取尺寸
            width, height = self.SIZE_MAP.get(size, (1024, 1024))

            # 构建风格增强 prompt
            style_prompts = {
                "modern": "modern design, clean, minimalist, professional",
                "minimal": "minimalist, simple, clean background, white",
                "lifestyle": "lifestyle photography, natural lighting, cozy",
                "product": "product photography, studio lighting, white background",
                "natural": "natural, realistic, authentic",
                "vivid": "vivid colors, high saturation, eye-catching",
            }

            enhanced_prompt = f"{prompt}, {style_prompts.get(style, style_prompts['modern'])}"

            # 生成 URL
            image_url = self._build_pollinations_url(
                prompt=enhanced_prompt,
                model=self.POLLINATIONS_MODELS.get(model, "openai"),
                width=width,
                height=height,
            )

            return ImageResult(
                url=image_url,
                prompt=enhanced_prompt,
                style=style,
                width=width,
                height=height,
                success=True,
            )

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return ImageResult(success=False, error="图片生成失败，请稍后重试")

    def generate_image_bytes(
        self,
        prompt: str,
        style: str = "modern",
        size: str = "square",
    ) -> bytes:
        """
        直接获取图片字节数据（用于保存到本地）

        Args:
            prompt: 图片描述
            style: 风格
            size: 尺寸

        Returns:
            bytes: 图片数据
        """
        try:
            import requests

            result = self.generate_image(prompt, style, size)
            if not result.success:
                raise Exception(result.error)

            response = requests.get(result.url, timeout=60)
            response.raise_for_status()

            return response.content

        except ImportError:
            logger.error("requests library not available")
            raise Exception("缺少 requests 库")
        except Exception as e:
            logger.error(f"Failed to get image bytes: {e}")
            raise

    def save_image(
        self,
        prompt: str,
        style: str = "modern",
        size: str = "square",
    ) -> ImageResult:
        """
        生成并保存图片到本地

        Args:
            prompt: 图片描述
            style: 风格
            size: 尺寸

        Returns:
            ImageResult: 包含本地路径的结果
        """
        try:
            image_bytes = self.generate_image_bytes(prompt, style, size)

            # 保存到本地
            filename = f"img-{uuid.uuid4().hex[:8]}.png"
            local_path = os.path.join(self.output_dir, filename)

            with open(local_path, "wb") as f:
                f.write(image_bytes)

            logger.success(f"Image saved: {local_path}")

            result = self.generate_image(prompt, style, size)
            result.local_path = local_path
            return result

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return ImageResult(success=False, error="图片保存失败")

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
                    style=ImageStyle.VIVID,
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
                    style=ImageStyle.NATURAL,
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
