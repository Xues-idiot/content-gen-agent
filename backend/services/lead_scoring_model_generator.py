"""
Vox Lead Scoring Model Generator Service 模块

潜在客户评分模型生成服务
- 评分标准
- 权重分配
- 分级定义
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class LeadScoringModelGeneratorService:
    """
    潜在客户评分模型生成服务

    生成潜在客户评分模型内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_lead_scoring_model(
        self,
        product_category: str,
        sales_team: str,
        num_criteria: int = 10,
    ) -> Dict[str, Any]:
        """
        生成潜在客户评分模型

        Args:
            product_category: 产品类别
            sales_team: 销售团队
            num_criteria: 标准数量

        Returns:
            Dict: 潜在客户评分模型
        """
        try:
            prompt = f"""请为{product_category}产品类别的{sales_team}团队生成{num_criteria}个标准的潜在客户评分模型。

请以JSON格式返回：
{{
    "product_category": "产品类别",
    "sales_team": "销售团队",
    "num_criteria": {num_criteria},
    "scoring_model_name": "评分模型名称",
    "demographic_criteria": [
        {{
            "criteria_name": "标准名称",
            "weight": "权重",
            "scoring_scale": "评分尺度"
        }}
    ],
    "behavioral_criteria": [
        {{
            "criteria_name": "标准名称",
            "weight": "权重",
            "scoring_scale": "评分尺度"
        }}
    ],
    "engagement_criteria": [
        {{
            "criteria_name": "标准名称",
            "weight": "权重",
            "scoring_scale": "评分尺度"
        }}
    ],
    "lead_tiers": [
        {{
            "tier_name": "层级名称",
            "score_range": "评分范围",
            "definition": "定义"
        }}
    ],
    "qualification_criteria": ["资质标准1"],
    "implementation_notes": "实施说明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_category": product_category,
                "sales_team": sales_team,
                "num_criteria": num_criteria,
                **result,
            }

        except Exception as e:
            logger.error(f"生成潜在客户评分模型失败: {e}")
            return {
                "product_category": product_category,
                "sales_team": sales_team,
                "num_criteria": num_criteria,
                "scoring_model_name": "",
                "demographic_criteria": [],
                "behavioral_criteria": [],
                "engagement_criteria": [],
                "lead_tiers": [],
                "qualification_criteria": [],
                "implementation_notes": "",
            }


lead_scoring_model_generator_service = LeadScoringModelGeneratorService()
