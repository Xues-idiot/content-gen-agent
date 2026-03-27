"""
Vox User Story Generator Service 模块

用户故事生成服务
- 用户需求
- 场景描述
- 成功标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class UserStoryGeneratorService:
    """
    用户故事生成服务

    生成用户故事内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_user_story(
        self,
        persona: str,
        goal: str,
        product_name: str = "产品",
    ) -> Dict[str, Any]:
        """
        生成用户故事

        Args:
            persona: 用户画像
            goal: 用户目标
            product_name: 产品名称

        Returns:
            Dict: 用户故事
        """
        try:
            prompt = f"""请为"{persona}"用户使用"{product_name}"实现"{goal}"生成用户故事。

请以JSON格式返回：
{{
    "persona": "用户画像",
    "goal": "用户目标",
    "product_name": "产品名称",
    "story_title": "故事标题",
    "story": "用户故事（As a... I want... So that...）",
    "acceptance_criteria": ["验收标准1"],
    "user_flow": ["用户流程1"],
    "pain_points": ["痛点1"],
    "success_metrics": "成功指标",
    "priority": "优先级",
    "notes": "备注"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "persona": persona,
                "goal": goal,
                "product_name": product_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成用户故事失败: {e}")
            return {
                "persona": persona,
                "goal": goal,
                "product_name": product_name,
                "story_title": "",
                "story": "",
                "acceptance_criteria": [],
                "user_flow": [],
                "pain_points": [],
                "success_metrics": "",
                "priority": "",
                "notes": "",
            }


user_story_generator_service = UserStoryGeneratorService()