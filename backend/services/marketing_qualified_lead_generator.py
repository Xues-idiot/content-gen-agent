"""
Vox Marketing Qualified Lead Generator Service 模块

营销合格线索生成服务
- MQL定义
- 资格标准
- 交接流程
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MarketingQualifiedLeadGeneratorService:
    """
    营销合格线索生成服务

    生成营销合格线索内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_marketing_qualified_lead(
        self,
        product_category: str,
        sales_team: str,
        num_criteria: int = 10,
    ) -> Dict[str, Any]:
        """
        生成营销合格线索

        Args:
            product_category: 产品类别
            sales_team: 销售团队
            num_criteria: 标准数量

        Returns:
            Dict: 营销合格线索
        """
        try:
            prompt = f"""请为{product_category}产品类别的{sales_team}团队生成{num_criteria}个标准的营销合格线索定义。

请以JSON格式返回：
{{
    "product_category": "产品类别",
    "sales_team": "销售团队",
    "num_criteria": {num_criteria},
    "mql_definition": "MQL定义",
    "demographic_criteria": ["人口统计标准1"],
    "behavioral_criteria": ["行为标准1"],
    "engagement_criteria": ["参与标准1"],
    "firmographic_criteria": ["公司特征标准1"],
    "scoring_threshold": "评分阈值",
    "lead_tiers": [
        {{
            "tier_name": "层级名称",
            "score_range": "评分范围",
            "characteristics": ["特征1"]
        }}
    ],
    "handoff_process": "交接流程",
    "sdr_involvement": "SDR参与",
    "success_metrics": ["成功指标1"]
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
            logger.error(f"生成营销合格线索失败: {e}")
            return {
                "product_category": product_category,
                "sales_team": sales_team,
                "num_criteria": num_criteria,
                "mql_definition": "",
                "demographic_criteria": [],
                "behavioral_criteria": [],
                "engagement_criteria": [],
                "firmographic_criteria": [],
                "scoring_threshold": "",
                "lead_tiers": [],
                "handoff_process": "",
                "sdr_involvement": "",
                "success_metrics": [],
            }


marketing_qualified_lead_generator_service = MarketingQualifiedLeadGeneratorService()
