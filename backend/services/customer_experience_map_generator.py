"""
Vox Customer Experience Map Generator Service 模块

客户体验地图生成服务
- 体验触点
- 情感曲线
- 优化机会
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerExperienceMapGeneratorService:
    """
    客户体验地图生成服务

    生成客户体验地图内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_experience_map(
        self,
        product_service: str,
        customer_segment: str,
        num_stages: int = 8,
    ) -> Dict[str, Any]:
        """
        生成客户体验地图

        Args:
            product_service: 产品/服务
            customer_segment: 客户细分
            num_stages: 阶段数量

        Returns:
            Dict: 客户体验地图
        """
        try:
            prompt = f"""请为"{product_service}"的{customer_segment}细分市场生成{num_stages}个阶段的客户体验地图。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "customer_segment": "客户细分",
    "num_stages": {num_stages},
    "experience_overview": "体验概述",
    "experience_stages": [
        {{
            "stage_name": "阶段名称",
            "touchpoints": ["触点1"],
            "customer_actions": ["客户行动1"],
            "emotions": ["情绪1"],
            "pain_points": ["痛点1"],
            "satisfaction_drivers": ["满意度驱动因素1"]
        }}
    ],
    "emotion_curve": ["情绪曲线1"],
    "critical_moments": ["关键时刻1"],
    "improvement_opportunities": ["改进机会1"],
    "quick_wins": ["快速见效1"],
    "strategic_initiatives": ["战略举措1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_service": product_service,
                "customer_segment": customer_segment,
                "num_stages": num_stages,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户体验地图失败: {e}")
            return {
                "product_service": product_service,
                "customer_segment": customer_segment,
                "num_stages": num_stages,
                "experience_overview": "",
                "experience_stages": [],
                "emotion_curve": [],
                "critical_moments": [],
                "improvement_opportunities": [],
                "quick_wins": [],
                "strategic_initiatives": [],
            }


customer_experience_map_generator_service = CustomerExperienceMapGeneratorService()
