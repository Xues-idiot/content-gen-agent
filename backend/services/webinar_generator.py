"""
Vox Webinar Description Generator Service 模块

网络研讨会生成服务
- 研讨会描述
- 邀请函
- 跟进邮件
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarGeneratorService:
    """
    网络研讨会生成服务

    生成 webinar 相关内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_content(
        self,
        topic: str,
        presenter: str,
    ) -> Dict[str, Any]:
        """
        生成研讨会内容

        Args:
            topic: 主题
            presenter: 主讲人

        Returns:
            Dict: 研讨会内容
        """
        try:
            prompt = f"""请为"{topic}"网络研讨会生成内容。

主讲人：{presenter}

请以JSON格式返回：
{{
    "title": "研讨会标题",
    "description": "描述",
    "agenda": ["议程1", "议程2"],
    "target_audience": "目标受众",
    "benefits": ["收获1", "收获2"]
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
                "presenter": presenter,
                **result,
            }

        except Exception as e:
            logger.error(f"生成研讨会内容失败: {e}")
            return {
                "topic": topic,
                "presenter": presenter,
                "title": "",
                "description": "",
                "agenda": [],
                "target_audience": "",
                "benefits": [],
            }


webinar_generator_service = WebinarGeneratorService()