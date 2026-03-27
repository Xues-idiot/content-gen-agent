"""
Vox Social Media Bio Generator Service 模块

社交媒体简介生成服务
- 个人简介
- 品牌简介
- Bio优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SocialMediaBioGeneratorService:
    """
    社交媒体简介生成服务

    生成社交媒体个人/品牌简介
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_bio(
        self,
        name: str,
        bio_type: str = "personal",
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成简介

        Args:
            name: 名称
            bio_type: 类型
            platform: 平台

        Returns:
            Dict: 简介内容
        """
        try:
            prompt = f"""请为"{name}"生成一个{platform}平台的{bio_type}类型简介。

请以JSON格式返回：
{{
    "bio": "简介正文",
    "hashtags": ["#标签1"],
    "emoji_suggestions": ["emoji1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "name": name,
                "bio_type": bio_type,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成简介失败: {e}")
            return {
                "name": name,
                "bio_type": bio_type,
                "platform": platform,
                "bio": "",
                "hashtags": [],
                "emoji_suggestions": [],
            }


social_media_bio_generator_service = SocialMediaBioGeneratorService()