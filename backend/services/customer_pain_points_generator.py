"""
Vox Customer Pain Points Generator Service 模块

客户痛点分析生成服务
- 痛点识别
- 情感驱动
- 解决方案映射
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerPainPointsGeneratorService:
    """
    客户痛点分析生成服务

    生成客户痛点分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_pain_points(
        self,
        industry: str,
        persona_type: str,
        num_pain_points: int = 5,
    ) -> Dict[str, Any]:
        """
        生成客户痛点分析

        Args:
            industry: 行业
            persona_type: 人物角色类型
            num_pain_points: 痛点数量

        Returns:
            Dict: 客户痛点分析
        """
        try:
            prompt = f"""请为{industry}行业的{persona_type}用户生成{num_pain_points}个客户痛点分析。

请以JSON格式返回：
{{
    "industry": "行业",
    "persona_type": "人物角色类型",
    "num_pain_points": {num_pain_points},
    "pain_points": [
        {{
            "pain_point": "痛点",
            "severity": "严重程度",
            "frequency": "频率",
            "emotional_trigger": "情感触发器",
            "financial_impact": "财务影响"
        }}
    ],
    "persona_details": {{
        "demographics": "人口统计",
        "goals": ["目标1"],
        "frustrations": ["挫折1"]
    }},
    "solution_mapping": [
        {{
            "pain_point": "痛点",
            "solution": "解决方案"
        }}
    ],
    "emotional_journey_map": "情感旅程图",
    "language_words": ["情感用词1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "industry": industry,
                "persona_type": persona_type,
                "num_pain_points": num_pain_points,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户痛点分析失败: {e}")
            return {
                "industry": industry,
                "persona_type": persona_type,
                "num_pain_points": num_pain_points,
                "pain_points": [],
                "persona_details": {},
                "solution_mapping": [],
                "emotional_journey_map": "",
                "language_words": [],
            }


customer_pain_points_generator_service = CustomerPainPointsGeneratorService()