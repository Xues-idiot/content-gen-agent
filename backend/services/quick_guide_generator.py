"""
Vox Quick Guide Generator Service 模块

快速入门指南生成服务
- 新手引导
- 基础教程
- 技巧提示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class QuickGuideGeneratorService:
    """
    快速入门指南生成服务

    生成快速入门指南内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_quick_guide(
        self,
        product_name: str,
        audience: str = "beginner",
        guide_length: str = "short",
    ) -> Dict[str, Any]:
        """
        生成快速入门指南

        Args:
            product_name: 产品名称
            audience: 目标受众
            guide_length: 指南长度

        Returns:
            Dict: 快速入门指南
        """
        try:
            prompt = f"""请为"{product_name}"生成快速入门指南（受众：{audience}，长度：{guide_length}）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "audience": "目标受众",
    "guide_length": "指南长度",
    "title": "指南标题",
    "overview": "概述",
    "prerequisites": ["前提条件1"],
    "steps": [
        {{
            "step_number": 1,
            "title": "步骤标题",
            "description": "步骤描述",
            "time_estimate": "预计时间",
            "tips": "小贴士"
        }}
    ],
    "common_first_steps": ["常见第一步1"],
    "pitfalls_to_avoid": ["需避免的坑1"],
    "next_steps": ["下一步1"],
    "help_resources": ["帮助资源1"]
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
                "audience": audience,
                "guide_length": guide_length,
                **result,
            }

        except Exception as e:
            logger.error(f"生成快速入门指南失败: {e}")
            return {
                "product_name": product_name,
                "audience": audience,
                "guide_length": guide_length,
                "title": "",
                "overview": "",
                "prerequisites": [],
                "steps": [],
                "common_first_steps": [],
                "pitfalls_to_avoid": [],
                "next_steps": [],
                "help_resources": [],
            }


quick_guide_generator_service = QuickGuideGeneratorService()