"""
Vox Product Backlog Generator Service 模块

产品待办列表生成服务
- 用户故事
- 优先级排序
- 估算
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductBacklogGeneratorService:
    """
    产品待办列表生成服务

    生成产品待办列表内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_backlog(
        self,
        product_name: str,
        sprint_theme: str,
        num_stories: int = 15,
    ) -> Dict[str, Any]:
        """
        生成产品待办列表

        Args:
            product_name: 产品名称
            sprint_theme: 冲刺主题
            num_stories: 故事数量

        Returns:
            Dict: 产品待办列表
        """
        try:
            prompt = f"""请为"{product_name}"产品生成以{sprint_theme}为主题的{num_stories}个用户故事的产品待办列表。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "sprint_theme": "冲刺主题",
    "num_stories": {num_stories},
    "backlog_overview": "待办列表概述",
    "user_stories": [
        {{
            "story_id": "故事ID",
            "story_title": "故事标题",
            "story_description": "故事描述（作为...我想...以便...）",
            "acceptance_criteria": ["验收标准1"],
            "story_points": "故事点数",
            "priority": "优先级",
            "related_epic": "相关史诗"
        }}
    ],
    "epics": ["史诗1"],
    "technical_debt_items": ["技术债务项目1"],
    "prioritization_rationale": "优先级排序理由"
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
                "sprint_theme": sprint_theme,
                "num_stories": num_stories,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品待办列表失败: {e}")
            return {
                "product_name": product_name,
                "sprint_theme": sprint_theme,
                "num_stories": num_stories,
                "backlog_overview": "",
                "user_stories": [],
                "epics": [],
                "technical_debt_items": [],
                "prioritization_rationale": "",
            }


product_backlog_generator_service = ProductBacklogGeneratorService()
