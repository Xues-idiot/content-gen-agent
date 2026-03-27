"""
Vox How-To Generator Service 模块

教程生成服务
- 步骤分解
- 教程结构
- 技巧提示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class HowToGeneratorService:
    """
    How-To教程生成服务

    生成步骤教程
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_howto(
        self,
        topic: str,
        difficulty: str = "medium",
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成教程

        Args:
            topic: 主题
            difficulty: 难度
            platform: 平台

        Returns:
            Dict: 教程内容
        """
        try:
            prompt = f"""请为"{topic}"生成一个教程。

难度：{difficulty}
平台：{platform}

请提供：
1. 教程标题
2. 步骤列表（5-8步）
3. 每步要点
4. 常见错误
5. 技巧提示

请以JSON格式返回：
{{
    "title": "教程标题",
    "steps": [
        {{
            "step": 1,
            "title": "步骤标题",
            "description": "步骤描述",
            "tips": "小技巧"
        }}
    ],
    "common_mistakes": ["错误1", "错误2"],
    "pro_tips": ["技巧1", "技巧2"]
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
                "difficulty": difficulty,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成教程失败: {e}")
            return {
                "topic": topic,
                "difficulty": difficulty,
                "platform": platform,
                "title": "",
                "steps": [],
                "common_mistakes": [],
                "pro_tips": [],
            }


howto_generator_service = HowToGeneratorService()