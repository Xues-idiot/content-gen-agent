"""
Vox User Guide Generator Service 模块

用户指南生成服务
- 产品指南
- 入门教程
- 高级技巧
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class UserGuideGeneratorService:
    """
    用户指南生成服务

    生成产品使用指南
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_guide(
        self,
        product_name: str,
        guide_type: str = "getting_started",
    ) -> Dict[str, Any]:
        """
        生成用户指南

        Args:
            product_name: 产品名称
            guide_type: 指南类型

        Returns:
            Dict: 指南内容
        """
        try:
            prompt = f"""请为"{product_name}"生成一个{guide_type}类型的用户指南。

请以JSON格式返回：
{{
    "title": "指南标题",
    "overview": "概述",
    "steps": [
        {{
            "step": 1,
            "title": "步骤标题",
            "description": "步骤描述",
            "image_suggestion": "配图建议"
        }}
    ],
    "tips": ["技巧1", "技巧2"],
    "troubleshooting": ["问题1:解决方案"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "guide_type": guide_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成用户指南失败: {e}")
            return {
                "product_name": product_name,
                "guide_type": guide_type,
                "title": "",
                "overview": "",
                "steps": [],
                "tips": [],
                "troubleshooting": [],
            }


user_guide_generator_service = UserGuideGeneratorService()