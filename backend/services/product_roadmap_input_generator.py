"""
Vox Product Roadmap Input Generator Service 模块

产品路线图输入生成服务
- 功能优先级
- 市场反馈
- 战略对齐
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductRoadmapInputGeneratorService:
    """
    产品路线图输入生成服务

    生成产品路线图输入内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_roadmap_input(
        self,
        product_name: str,
        planning_horizon: str,
        num_features: int = 10,
    ) -> Dict[str, Any]:
        """
        生成产品路线图输入

        Args:
            product_name: 产品名称
            planning_horizon: 规划周期
            num_features: 功能数量

        Returns:
            Dict: 产品路线图输入
        """
        try:
            prompt = f"""请为"{product_name}"生成{planning_horizon}规划的{num_features}个功能的产品路线图输入。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "planning_horizon": "规划周期",
    "num_features": {num_features},
    "strategic_alignment": "战略对齐",
    "feature_prioritization": [
        {{
            "feature_name": "功能名称",
            "priority_rank": "优先级排名",
            "priority_rationale": "优先级理由",
            "customer_request_frequency": "客户请求频率",
            "development_effort": "开发工作量",
            "expected_impact": "预期影响"
        }}
    ],
    "customer_feedback_summary": "客户反馈摘要",
    "competitive_requirements": ["竞争需求1"],
    "technical_constraints": "技术约束",
    "recommended_timeline": "推荐时间线",
    "success_criteria": ["成功标准1"]
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
                "planning_horizon": planning_horizon,
                "num_features": num_features,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品路线图输入失败: {e}")
            return {
                "product_name": product_name,
                "planning_horizon": planning_horizon,
                "num_features": num_features,
                "strategic_alignment": "",
                "feature_prioritization": [],
                "customer_feedback_summary": "",
                "competitive_requirements": [],
                "technical_constraints": "",
                "recommended_timeline": "",
                "success_criteria": [],
            }


product_roadmap_input_generator_service = ProductRoadmapInputGeneratorService()
