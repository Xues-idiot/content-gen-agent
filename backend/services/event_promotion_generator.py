"""
Vox Event Promotion Generator Service 模块

活动推广生成服务
- 活动宣传
- 邀请函
- 倒计时文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EventPromotionGeneratorService:
    """
    活动推广生成服务

    生成活动宣传内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_promotion(
        self,
        event_name: str,
        event_type: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成活动推广

        Args:
            event_name: 活动名称
            event_type: 活动类型
            platform: 平台

        Returns:
            Dict: 推广内容
        """
        try:
            prompt = f"""请为"{event_name}"生成活动推广内容。

类型：{event_type}
平台：{platform}

请以JSON格式返回：
{{
    "title": "推广标题",
    "description": "活动描述",
    "highlights": ["亮点1", "亮点2"],
    "cta": "行动号召",
    "hashtags": ["#标签1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "event_name": event_name,
                "event_type": event_type,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成活动推广失败: {e}")
            return {
                "event_name": event_name,
                "event_type": event_type,
                "platform": platform,
                "title": "",
                "description": "",
                "highlights": [],
                "cta": "",
                "hashtags": [],
            }


event_promotion_generator_service = EventPromotionGeneratorService()