"""
Vox Caption Generator Service 模块

文案生成服务
- 多平台文案生成
- 风格适配
- 长度变体
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CaptionGeneratorService:
    """
    文案生成服务

    生成各平台的文案
    """

    def __init__(self):
        self.llm = llm_service

    # 平台文案风格
    PLATFORM_STYLES = {
        "xiaohongshu": {
            "length": "50-500字",
            "style": "种草分享、真实亲切",
            "elements": ["个人体验", "痛点解决", "效果展示"],
        },
        "tiktok": {
            "length": "15-100字",
            "style": "冲击、抓人、有节奏",
            "elements": ["悬念", "情绪", "行动号召"],
        },
        "weibo": {
            "length": "50-200字",
            "style": "观点鲜明、有话题性",
            "elements": ["观点", "话题标签", "互动引导"],
        },
        "official": {
            "length": "100-500字",
            "style": "专业、严谨、有价值",
            "elements": ["专业知识", "数据支撑", "行业洞察"],
        },
    }

    # 文案风格
    CAPTION_STYLES = {
        "casual": "轻松随意、朋友分享感",
        "professional": "专业严谨、行业分析感",
        "humorous": "幽默风趣、轻松搞笑",
        "emotional": "情感充沛、打动人心",
        "educational": "教育科普、干货分享",
        "inspirational": "励志鼓舞、正能量",
    }

    async def generate_caption(
        self,
        content_type: str,
        topic: str,
        platform: str = "xiaohongshu",
        style: str = "casual",
        length: str = "medium",
    ) -> Dict[str, Any]:
        """
        生成文案

        Args:
            content_type: 内容类型
            topic: 话题
            platform: 平台
            style: 风格
            length: 长度

        Returns:
            Dict: 生成的文案
        """
        try:
            prompt = f"""请为{platform}平台生成一条{content_type}类型的文案。

话题：{topic}
风格：{style}
长度：{length}

要求：
1. 符合{platform}平台风格
2. {self.PLATFORM_STYLES.get(platform, {}).get('style', '')}
3. {self.CAPTION_STYLES.get(style, '')}

请提供：
1. 主文案
2. 可选的简短版本
3. 建议的hashtag（3-5个）
4. 建议的emoji（2-3个）

请以JSON格式返回：
{{
    "main_caption": "主文案内容",
    "short_version": "简短版本",
    "hashtags": ["#标签1", "#标签2"],
    "emojis": ["emoji1", "emoji2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "content_type": content_type,
                "topic": topic,
                "platform": platform,
                "style": style,
                **result,
            }

        except Exception as e:
            logger.error(f"生成文案失败: {e}")
            return {
                "content_type": content_type,
                "topic": topic,
                "platform": platform,
                "style": style,
                "main_caption": "",
                "short_version": "",
                "hashtags": [],
                "emojis": [],
            }

    async def adapt_caption(
        self,
        original_caption: str,
        from_platform: str,
        to_platform: str,
    ) -> Dict[str, Any]:
        """
        适配文案

        将文案适配到不同平台

        Args:
            original_caption: 原始文案
            from_platform: 源平台
            to_platform: 目标平台

        Returns:
            Dict: 适配后的文案
        """
        try:
            prompt = f"""请将以下{from_platform}平台的文案适配到{to_platform}平台。

源平台：{from_platform}
目标平台：{to_platform}
原文案：{original_caption}

请以JSON格式返回：
{{
    "adapted_caption": "适配后的文案",
    "changes": ["改动点1", "改动点2"],
    "tips": ["适配建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "original_caption": original_caption,
                "from_platform": from_platform,
                "to_platform": to_platform,
                "adapted_caption": result.get("adapted_caption", ""),
                "changes": result.get("changes", []),
                "tips": result.get("tips", []),
            }

        except Exception as e:
            logger.error(f"适配文案失败: {e}")
            return {
                "original_caption": original_caption,
                "from_platform": from_platform,
                "to_platform": to_platform,
                "adapted_caption": original_caption,
                "changes": [],
                "tips": [],
            }

    def get_platform_styles(self) -> Dict[str, Any]:
        """
        获取平台风格

        Returns:
            Dict: 平台风格
        """
        return self.PLATFORM_STYLES

    def get_caption_styles(self) -> Dict[str, str]:
        """
        获取文案风格

        Returns:
            Dict: 文案风格
        """
        return self.CAPTION_STYLES


# 全局实例
caption_generator_service = CaptionGeneratorService()


if __name__ == "__main__":
    import asyncio

    service = CaptionGeneratorService()

    async def test():
        print("=== 生成文案 ===")
        result = await service.generate_caption(
            "好物推荐", "面霜测评", "xiaohongshu", "casual", "medium"
        )
        print(f"主文案: {result['main_caption'][:50]}...")
        print(f"Hashtags: {', '.join(result['hashtags'][:3])}")

        print("\n=== 适配文案 ===")
        adapted = await service.adapt_caption(
            "小红书文案内容",
            "xiaohongshu",
            "tiktok"
        )
        print(f"适配后: {adapted['adapted_caption'][:50]}...")

    asyncio.run(test())