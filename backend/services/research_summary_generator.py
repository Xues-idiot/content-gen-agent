"""
Vox Research Summary Generator Service 模块

研究报告摘要生成服务
- 研究要点
- 方法论
- 结论建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ResearchSummaryGeneratorService:
    """
    研究报告摘要生成服务

    生成研究报告摘要内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_research_summary(
        self,
        research_title: str,
        research_field: str,
        methodology: str = "quantitative",
    ) -> Dict[str, Any]:
        """
        生成研究报告摘要

        Args:
            research_title: 研究标题
            research_field: 研究领域
            methodology: 研究方法

        Returns:
            Dict: 研究报告摘要
        """
        try:
            prompt = f"""请为"{research_title}"（领域：{research_field}，方法：{methodology}）生成研究报告摘要。

请以JSON格式返回：
{{
    "research_title": "研究标题",
    "research_field": "研究领域",
    "methodology": "研究方法",
    "executive_summary": "执行摘要",
    "research_objectives": ["研究目标1"],
    "key_findings": ["关键发现1"],
    "data_sources": ["数据来源1"],
    "sample_size": "样本量",
    "limitations": ["研究局限性1"],
    "implications": ["研究意义1"],
    "recommendations": ["建议1"],
    "future_research": "未来研究方向"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "research_title": research_title,
                "research_field": research_field,
                "methodology": methodology,
                **result,
            }

        except Exception as e:
            logger.error(f"生成研究报告摘要失败: {e}")
            return {
                "research_title": research_title,
                "research_field": research_field,
                "methodology": methodology,
                "executive_summary": "",
                "research_objectives": [],
                "key_findings": [],
                "data_sources": [],
                "sample_size": "",
                "limitations": [],
                "implications": [],
                "recommendations": [],
                "future_research": "",
            }


research_summary_generator_service = ResearchSummaryGeneratorService()