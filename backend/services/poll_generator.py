"""
Vox Poll Generator Service 模块

投票生成服务
- 互动投票
- 问题设置
- 选项设计
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PollGeneratorService:
    """
    投票生成服务

    生成互动投票
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_poll(
        self,
        topic: str,
        num_options: int = 4,
        platform: str = "weibo",
    ) -> Dict[str, Any]:
        """
        生成投票

        Args:
            topic: 主题
            num_options: 选项数量
            platform: 平台

        Returns:
            Dict: 投票内容
        """
        try:
            prompt = f"""请为"{topic}"生成一个投票。

平台：{platform}
选项数：{num_options}

请以JSON格式返回：
{{
    "question": "投票问题",
    "options": ["选项1", "选项2"],
    "duration_days": 7,
    "add_poll_note": "补充说明"
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
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成投票失败: {e}")
            return {
                "topic": topic,
                "platform": platform,
                "question": "",
                "options": [],
                "duration_days": 7,
                "add_poll_note": "",
            }


poll_generator_service = PollGeneratorService()