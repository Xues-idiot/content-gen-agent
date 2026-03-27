"""
Vox Research Report Generator Service 模块

研究报告生成服务
- 研究发现
- 数据分析
- 结论建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ResearchReportGeneratorService:
    """
    研究报告生成服务

    生成研究报告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_research_report(
        self,
        research_topic: str,
        research_type: str,
        methodology: str,
    ) -> Dict[str, Any]:
        """
        生成研究报告

        Args:
            research_topic: 研究主题
            research_type: 研究类型
            methodology: 方法论

        Returns:
            Dict: 研究报告
        """
        try:
            prompt = f"""请为"{research_topic}"生成{research_type}类型的研究报告（方法：{methodology}）。

请以JSON格式返回：
{{
    "title": "标题",
    "research_topic": "研究主题",
    "research_type": "研究类型",
    "methodology": "方法论",
    "executive_summary": "执行摘要",
    "table_of_contents": "目录",
    "introduction": {{
        "background": "背景",
        "research_questions": ["研究问题1"],
        "hypotheses": ["假设1"]
    }},
    "literature_review": "文献综述",
    "findings": [
        {{
            "section": "章节",
            "data": "数据",
            "analysis": "分析"
        }}
    ],
    "data_presentation": "数据展示",
    "statistical_analysis": "统计分析",
    "qualitative_analysis": "定性分析",
    "discussion": "讨论",
    "limitations": "局限性",
    "implications": "影响",
    "recommendations": ["建议1"],
    "future_research": "未来研究",
    "references": ["参考文献1"],
    "appendices": ["附录1"],
    "author_notes": "作者备注"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "research_topic": research_topic,
                "research_type": research_type,
                "methodology": methodology,
                **result,
            }

        except Exception as e:
            logger.error(f"生成研究报告失败: {e}")
            return {
                "research_topic": research_topic,
                "research_type": research_type,
                "methodology": methodology,
                "title": "",
                "executive_summary": "",
                "table_of_contents": "",
                "introduction": {},
                "literature_review": "",
                "findings": [],
                "data_presentation": "",
                "statistical_analysis": "",
                "qualitative_analysis": "",
                "discussion": "",
                "limitations": "",
                "implications": "",
                "recommendations": [],
                "future_research": "",
                "references": [],
                "appendices": [],
                "author_notes": "",
            }


research_report_generator_service = ResearchReportGeneratorService()