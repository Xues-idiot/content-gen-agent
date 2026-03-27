"""
Vox Community Post Generator Service 模块

社区帖子生成服务
- 社区内容
- 互动帖子
- 话题讨论
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CommunityPostGeneratorService:
    """
    社区帖子生成服务

    生成社区帖子内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_community_post(
        self,
        platform: str,
        topic: str,
        post_type: str = "discussion",
    ) -> Dict[str, Any]:
        """
        生成社区帖子

        Args:
            platform: 平台
            topic: 主题
            post_type: 帖子类型

        Returns:
            Dict: 社区帖子
        """
        try:
            prompt = f"""请为{platform}社区生成关于"{topic}"的{post_type}类型帖子。

请以JSON格式返回：
{{
    "platform": "平台",
    "topic": "主题",
    "post_type": "帖子类型",
    "title": "帖子标题",
    "body": "帖子正文",
    "discussion_questions": ["讨论问题1"],
    "engagement_tips": ["互动技巧1"],
    "hashtags": ["标签1"],
    "optimal_posting_time": "最佳发布时间",
    "moderation_notes": "管理注意事项"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "platform": platform,
                "topic": topic,
                "post_type": post_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成社区帖子失败: {e}")
            return {
                "platform": platform,
                "topic": topic,
                "post_type": post_type,
                "title": "",
                "body": "",
                "discussion_questions": [],
                "engagement_tips": [],
                "hashtags": [],
                "optimal_posting_time": "",
                "moderation_notes": "",
            }


community_post_generator_service = CommunityPostGeneratorService()