"""
Vox Customer Loyalty Assessment Generator Service 模块

客户忠诚度评估生成服务
- 忠诚度指标
- 参与度评分
- 改进建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerLoyaltyAssessmentGeneratorService:
    """
    客户忠诚度评估生成服务

    生成客户忠诚度评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_loyalty_assessment(
        self,
        customer_name: str,
        assessment_period: str,
        num_metrics: int = 10,
    ) -> Dict[str, Any]:
        """
        生成客户忠诚度评估

        Args:
            customer_name: 客户名称
            assessment_period: 评估周期
            num_metrics: 指标数量

        Returns:
            Dict: 客户忠诚度评估
        """
        try:
            prompt = f"""请为"{customer_name}"生成{assessment_period}的客户忠诚度评估（{num_metrics}个指标）。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "assessment_period": "评估周期",
    "num_metrics": {num_metrics},
    "loyalty_score": "忠诚度评分",
    "nps_score": "NPS评分",
    "retention_rate": "留存率",
    "engagement_metrics": {{
        "purchase_frequency": "购买频率",
        "average_order_value": "平均订单价值",
        "product_range purchased": "购买产品范围"
    }},
    "sentiment_analysis": "情感分析",
    "recommendation_behavior": "推荐行为",
    "loyalty_program_participation": "忠诚度计划参与度",
    "risk_indicators": ["风险指标1"],
    "strengths": ["优势1"],
    "improvement_areas": ["改进领域1"],
    "recommended_actions": ["推荐行动1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "customer_name": customer_name,
                "assessment_period": assessment_period,
                "num_metrics": num_metrics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户忠诚度评估失败: {e}")
            return {
                "customer_name": customer_name,
                "assessment_period": assessment_period,
                "num_metrics": num_metrics,
                "loyalty_score": "",
                "nps_score": "",
                "retention_rate": "",
                "engagement_metrics": {},
                "sentiment_analysis": "",
                "recommendation_behavior": "",
                "loyalty_program_participation": "",
                "risk_indicators": [],
                "strengths": [],
                "improvement_areas": [],
                "recommended_actions": [],
            }


customer_loyalty_assessment_generator_service = CustomerLoyaltyAssessmentGeneratorService()
