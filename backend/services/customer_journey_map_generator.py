"""
Vox Customer Journey Map Generator Service 模块

客户旅程地图生成服务
- 触点分析
- 体验优化
- 转化路径
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerJourneyMapGeneratorService:
    """
    客户旅程地图生成服务

    生成客户旅程地图内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_journey_map(
        self,
        product_name: str,
        target_audience: str,
        num_stages: int = 5,
    ) -> Dict[str, Any]:
        """
        生成客户旅程地图

        Args:
            product_name: 产品名称
            target_audience: 目标受众
            num_stages: 阶段数量

        Returns:
            Dict: 客户旅程地图
        """
        try:
            prompt = f"""请为"{product_name}"为"{target_audience}"生成{num_stages}阶段客户旅程地图。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "target_audience": "目标受众",
    "num_stages": 阶段数,
    "overview": "概述",
    "persona": "用户画像",
    "stages": [
        {{
            "stage_name": "阶段名称",
            "stage_order": 顺序,
            "description": "描述",
            "touchpoints": ["触点1"],
            "customer_actions": ["客户动作1"],
            "customer_thoughts": ["客户想法1"],
            "emotions": ["情绪1"],
            "pain_points": ["痛点1"],
            "opportunities": ["机会1"],
            "channels": ["渠道1"],
            "support_needed": "所需支持"
        }}
    ],
    "key_insights": ["关键洞察1"],
    "improvement_areas": ["改进领域1"],
    "quick_wins": ["快速见效1"],
    "strategic_initiatives": ["战略性举措1"]
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
                "target_audience": target_audience,
                "num_stages": num_stages,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户旅程地图失败: {e}")
            return {
                "product_name": product_name,
                "target_audience": target_audience,
                "num_stages": num_stages,
                "overview": "",
                "persona": "",
                "stages": [],
                "key_insights": [],
                "improvement_areas": [],
                "quick_wins": [],
                "strategic_initiatives": [],
            }


customer_journey_map_generator_service = CustomerJourneyMapGeneratorService()