"""
Vox Business Plan Generator Service 模块

商业计划生成服务
- 市场分析
- 商业模式
- 财务预测
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BusinessPlanGeneratorService:
    """
    商业计划生成服务

    生成商业计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_business_plan(
        self,
        company_name: str,
        industry: str,
        stage: str = "startup",
    ) -> Dict[str, Any]:
        """
        生成商业计划

        Args:
            company_name: 公司名称
            industry: 行业
            stage: 阶段

        Returns:
            Dict: 商业计划
        """
        try:
            prompt = f"""请为"{company_name}"（{industry}行业，阶段：{stage}）生成商业计划。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "industry": "行业",
    "stage": "阶段",
    "executive_summary": "执行摘要",
    "problem_statement": "问题陈述",
    "solution": "解决方案",
    "market_analysis": "市场分析",
    "business_model": "商业模式",
    "competitive_advantage": "竞争优势",
    "target_customers": ["目标客户1"],
    "marketing_strategy": "营销策略",
    "team_overview": "团队概述",
    "financial_projections": "财务预测",
    "funding_requirements": "资金需求",
    "use_of_funds": "资金用途"
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
                "industry": industry,
                "stage": stage,
                **result,
            }

        except Exception as e:
            logger.error(f"生成商业计划失败: {e}")
            return {
                "company_name": company_name,
                "industry": industry,
                "stage": stage,
                "executive_summary": "",
                "problem_statement": "",
                "solution": "",
                "market_analysis": "",
                "business_model": "",
                "competitive_advantage": "",
                "target_customers": [],
                "marketing_strategy": "",
                "team_overview": "",
                "financial_projections": "",
                "funding_requirements": "",
                "use_of_funds": "",
            }


business_plan_generator_service = BusinessPlanGeneratorService()