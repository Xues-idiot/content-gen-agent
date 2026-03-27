"""
Vox Client Health Score Generator Service 模块

客户健康评分生成服务
- 评分指标
- 评分标准
- 健康状态
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ClientHealthScoreGeneratorService:
    """
    客户健康评分生成服务

    生成客户健康评分内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_client_health_score(
        self,
        client_name: str,
        account_age_months: int,
        num_metrics: int = 5,
    ) -> Dict[str, Any]:
        """
        生成客户健康评分

        Args:
            client_name: 客户名称
            account_age_months: 账户年龄（月）
            num_metrics: 指标数量

        Returns:
            Dict: 客户健康评分
        """
        try:
            prompt = f"""请为"{client_name}"（账户年龄：{account_age_months}个月）生成{num_metrics}个指标的客户健康评分。

请以JSON格式返回：
{{
    "client_name": "客户名称",
    "account_age_months": {account_age_months},
    "num_metrics": {num_metrics},
    "overall_health_score": "总体健康评分",
    "health_status": "健康状态",
    "metrics": [
        {{
            "metric_name": "指标名称",
            "score": "评分",
            "weight": "权重",
            "status": "状态",
            "recommendations": ["建议1"]
        }}
    ],
    "risk_factors": ["风险因素1"],
    "improvement_suggestions": ["改进建议1"],
    "next_review_date": "下次审查日期"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "client_name": client_name,
                "account_age_months": account_age_months,
                "num_metrics": num_metrics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户健康评分失败: {e}")
            return {
                "client_name": client_name,
                "account_age_months": account_age_months,
                "num_metrics": num_metrics,
                "overall_health_score": "",
                "health_status": "",
                "metrics": [],
                "risk_factors": [],
                "improvement_suggestions": [],
                "next_review_date": "",
            }


client_health_score_generator_service = ClientHealthScoreGeneratorService()