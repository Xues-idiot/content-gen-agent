"""
Vox Customer Success Metrics Generator Service 模块

客户成功指标生成服务
- 健康评分
- 成功基准
- 预警系统
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerSuccessMetricsGeneratorService:
    """
    客户成功指标生成服务

    生成客户成功指标内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_success_metrics(
        self,
        product_category: str,
        customer_segment: str,
        num_metrics: int = 10,
    ) -> Dict[str, Any]:
        """
        生成客户成功指标

        Args:
            product_category: 产品类别
            customer_segment: 客户细分
            num_metrics: 指标数量

        Returns:
            Dict: 客户成功指标
        """
        try:
            prompt = f"""请为{product_category}产品的{customer_segment}细分市场生成{num_metrics}个指标的客户成功指标体系。

请以JSON格式返回：
{{
    "product_category": "产品类别",
    "customer_segment": "客户细分",
    "num_metrics": {num_metrics},
    "metrics_framework": "指标框架",
    "key_metrics": [
        {{
            "metric_name": "指标名称",
            "definition": "定义",
            "calculation_method": "计算方法",
            "benchmark_value": "基准值",
            "target_value": "目标值"
        }}
    ],
    "health_score_model": {{
        "scoring_algorithm": "评分算法",
        "weighting_factors": ["权重因素1"],
        "score_interpretation": "分数解释"
    }},
    "early_warning_indicators": ["早期预警指标1"],
    "success_benchmarks": "成功基准",
    "reporting_frequency": "报告频率",
    "action_thresholds": "行动阈值"
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
                "customer_segment": customer_segment,
                "num_metrics": num_metrics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户成功指标失败: {e}")
            return {
                "product_category": product_category,
                "customer_segment": customer_segment,
                "num_metrics": num_metrics,
                "metrics_framework": "",
                "key_metrics": [],
                "health_score_model": {},
                "early_warning_indicators": [],
                "success_benchmarks": "",
                "reporting_frequency": "",
                "action_thresholds": "",
            }


customer_success_metrics_generator_service = CustomerSuccessMetricsGeneratorService()
