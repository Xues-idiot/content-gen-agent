"""
Vox Sales Qualification Framework Generator Service 模块

销售资格框架生成服务
- BANT标准
- 资格问题
- 评估矩阵
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesQualificationFrameworkGeneratorService:
    """
    销售资格框架生成服务

    生成销售资格框架内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_qualification_framework(
        self,
        product_service: str,
        target_segment: str,
        num_criteria: int = 8,
    ) -> Dict[str, Any]:
        """
        生成销售资格框架

        Args:
            product_service: 产品/服务
            target_segment: 目标细分
            num_criteria: 标准数量

        Returns:
            Dict: 销售资格框架
        """
        try:
            prompt = f"""请为"{product_service}"的{target_segment}细分市场生成{num_criteria}个标准的销售资格框架。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "target_segment": "目标细分",
    "num_criteria": {num_criteria},
    "framework_name": "框架名称",
    "qualification_criteria": [
        {{
            "criterion": "标准",
            "weight": "权重",
            "assessment_questions": ["评估问题1"],
            "pass_threshold": "通过阈值"
        }}
    ],
    "budget_qualification": "预算资格",
    "authority_qualification": "权威资格",
    "timeline_qualification": "时间线资格",
    "need_qualification": "需求资格",
    "scoring_matrix": "评分矩阵",
    "disqualification_reasons": ["取消资格原因1"],
    "next_steps_by_score": "按评分的下一步"
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
                "target_segment": target_segment,
                "num_criteria": num_criteria,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售资格框架失败: {e}")
            return {
                "product_service": product_service,
                "target_segment": target_segment,
                "num_criteria": num_criteria,
                "framework_name": "",
                "qualification_criteria": [],
                "budget_qualification": "",
                "authority_qualification": "",
                "timeline_qualification": "",
                "need_qualification": "",
                "scoring_matrix": "",
                "disqualification_reasons": [],
                "next_steps_by_score": "",
            }


sales_qualification_framework_generator_service = SalesQualificationFrameworkGeneratorService()
