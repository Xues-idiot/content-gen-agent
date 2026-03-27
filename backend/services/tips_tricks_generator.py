"""
Vox Tips and Tricks Generator Service 模块

技巧提示生成服务
- 小技巧集合
- 实用建议
- 隐藏功能
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TipsAndTricksGeneratorService:
    """
    技巧提示生成服务

    生成实用技巧内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_tips(
        self,
        topic: str,
        num_tips: int = 5,
        difficulty: str = "beginner",
    ) -> List[Dict[str, Any]]:
        """
        生成技巧

        Args:
            topic: 主题
            num_tips: 技巧数量
            difficulty: 难度

        Returns:
            List[Dict]: 技巧列表
        """
        try:
            prompt = f"""请为"{topic}"生成{num_tips}个{difficulty}级别的技巧。

请以JSON格式返回：
{{
    "tips": [
        {{
            "title": "技巧标题",
            "description": "技巧描述",
            "difficulty": "难度",
            "time_save": "节省时间"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return result.get("tips", [])

        except Exception as e:
            logger.error(f"生成技巧失败: {e}")
            return []


tips_and_tricks_generator_service = TipsAndTricksGeneratorService()