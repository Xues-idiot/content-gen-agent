"""
Vox Demo Effectiveness Evaluation Generator Service 模块

演示有效性评估生成服务
- 演示指标
- 反馈分析
- 改进建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DemoEffectivenessEvaluationGeneratorService:
    """
    演示有效性评估生成服务

    生成演示有效性评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_demo_effectiveness_evaluation(
        self,
        demo_name: str,
        product_name: str,
        num_metrics: int = 8,
    ) -> Dict[str, Any]:
        """
        生成演示有效性评估

        Args:
            demo_name: 演示名称
            product_name: 产品名称
            num_metrics: 指标数量

        Returns:
            Dict: 演示有效性评估
        """
        try:
            prompt = f"""请为"{demo_name}"演示（产品：{product_name}）生成{num_metrics}个指标的有效性评估。

请以JSON格式返回：
{{
    "demo_name": "演示名称",
    "product_name": "产品名称",
    "num_metrics": {num_metrics},
    "evaluation_summary": "评估摘要",
    "effectiveness_metrics": [
        {{
            "metric_name": "指标名称",
            "score": "评分",
            "benchmark": "基准",
            "improvement_needed": "需要改进"
        }}
    ],
    "audience_feedback": ["受众反馈1"],
    "engagement_level": "参与度水平",
    "message_clarity": "信息清晰度",
    "technical_performance": "技术性能",
    "key_strengths": ["关键优势1"],
    "areas_for_improvement": ["改进领域1"],
    "recommended_adjustments": ["推荐调整1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "demo_name": demo_name,
                "product_name": product_name,
                "num_metrics": num_metrics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成演示有效性评估失败: {e}")
            return {
                "demo_name": demo_name,
                "product_name": product_name,
                "num_metrics": num_metrics,
                "evaluation_summary": "",
                "effectiveness_metrics": [],
                "audience_feedback": [],
                "engagement_level": "",
                "message_clarity": "",
                "technical_performance": "",
                "key_strengths": [],
                "areas_for_improvement": [],
                "recommended_adjustments": [],
            }


demo_effectiveness_evaluation_generator_service = DemoEffectivenessEvaluationGeneratorService()
