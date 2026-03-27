"""
Vox Annual Report Generator Service 模块

年度报告生成服务
- 年度总结
- 成就回顾
- 数据报告
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AnnualReportGeneratorService:
    """
    年度报告生成服务

    生成年度报告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_annual_report(
        self,
        company_name: str,
        year: int,
    ) -> Dict[str, Any]:
        """
        生成年度报告

        Args:
            company_name: 公司名称
            year: 年份

        Returns:
            Dict: 年度报告
        """
        try:
            prompt = f"""请为"{company_name}"生成{year}年年度报告。

请以JSON格式返回：
{{
    "title": "报告标题",
    "executive_summary": "执行摘要",
    "achievements": ["成就1", "成就2"],
    "milestones": ["里程碑1"],
    "team_acknowledgment": "团队致谢",
    "looking_ahead": "未来展望"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_name": company_name,
                "year": year,
                **result,
            }

        except Exception as e:
            logger.error(f"生成年度报告失败: {e}")
            return {
                "company_name": company_name,
                "year": year,
                "title": "",
                "executive_summary": "",
                "achievements": [],
                "milestones": [],
                "team_acknowledgment": "",
                "looking_ahead": "",
            }


annual_report_generator_service = AnnualReportGeneratorService()