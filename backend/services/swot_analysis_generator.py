"""
Vox SWOT Analysis Generator Service 模块

SWOT分析生成服务
- 优势分析
- 劣势分析
- 机会分析
- 威胁分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SWOTAnalysisGeneratorService:
    """
    SWOT分析生成服务

    生成SWOT分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_swot_analysis(
        self,
        subject_name: str,
        subject_type: str = "company",
        industry: str = "",
    ) -> Dict[str, Any]:
        """
        生成SWOT分析

        Args:
            subject_name: 分析对象名称
            subject_type: 分析对象类型
            industry: 行业

        Returns:
            Dict: SWOT分析
        """
        try:
            industry_context = f"，行业：{industry}" if industry else ""
            prompt = f"""请为"{subject_name}"（类型：{subject_type}{industry_context}）生成SWOT分析。

请以JSON格式返回：
{{
    "subject_name": "分析对象名称",
    "subject_type": "分析对象类型",
    "industry": "行业",
    "strengths": [
        {{
            "item": "优势",
            "impact": "影响程度",
            "description": "描述"
        }}
    ],
    "weaknesses": [
        {{
            "item": "劣势",
            "impact": "影响程度",
            "description": "描述"
        }}
    ],
    "opportunities": [
        {{
            "item": "机会",
            "potential": "潜力",
            "timeline": "时间范围"
        }}
    ],
    "threats": [
        {{
            "item": "威胁",
            "likelihood": "可能性",
            "potential_impact": "潜在影响"
        }}
    ],
    "strategic_recommendations": ["战略建议1"],
    "overall_assessment": "整体评估"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "subject_name": subject_name,
                "subject_type": subject_type,
                "industry": industry,
                **result,
            }

        except Exception as e:
            logger.error(f"生成SWOT分析失败: {e}")
            return {
                "subject_name": subject_name,
                "subject_type": subject_type,
                "industry": industry,
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": [],
                "strategic_recommendations": [],
                "overall_assessment": "",
            }


swot_analysis_generator_service = SWOTAnalysisGeneratorService()