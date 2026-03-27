"""
Vox LinkedIn Post Generator Service 模块

LinkedIn帖子生成服务
- 专业内容生成
- 个人品牌
- 行业洞察
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class LinkedInPostGeneratorService:
    """
    LinkedIn帖子生成服务

    生成LinkedIn专业内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_post(
        self,
        topic: str,
        post_type: str = "insight",
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """
        生成LinkedIn帖子

        Args:
            topic: 主题
            post_type: 帖子类型
            tone: 语气

        Returns:
            Dict: 帖子内容
        """
        try:
            prompt = f"""请为LinkedIn生成一个关于"{topic}"的帖子。

类型：{post_type}
语气：{tone}

请以JSON格式返回：
{{
    "content": "帖子正文",
    "hashtags": ["#标签1"],
    "call_to_action": "互动引导"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "topic": topic,
                "post_type": post_type,
                "tone": tone,
                **result,
            }

        except Exception as e:
            logger.error(f"生成LinkedIn帖子失败: {e}")
            return {
                "topic": topic,
                "post_type": post_type,
                "tone": tone,
                "content": "",
                "hashtags": [],
                "call_to_action": "",
            }


linkedin_post_generator_service = LinkedInPostGeneratorService()