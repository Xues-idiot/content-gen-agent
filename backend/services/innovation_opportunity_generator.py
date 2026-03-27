"""
Vox Innovation Opportunity Generator Service 模块

创新机会生成服务
- 趋势分析
- 技术洞察
- 创意构思
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InnovationOpportunityGeneratorService:
    """
    创新机会生成服务

    生成创新机会内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_innovation_opportunity(
        self,
        industry: str,
        focus_area: str,
        num_opportunities: int = 8,
    ) -> Dict[str, Any]:
        """
        生成创新机会

        Args:
            industry: 行业
            focus_area: 专注领域
            num_opportunities: 机会数量

        Returns:
            Dict: 创新机会
        """
        try:
            prompt = f"""请为{industry}行业的{focus_area}领域生成{num_opportunities}个创新机会。

请以JSON格式返回：
{{
    "industry": "行业",
    "focus_area": "专注领域",
    "num_opportunities": {num_opportunities},
    "executive_summary": "执行摘要",
    "emerging_trends": ["新兴趋势1"],
    "technology_insights": ["技术洞察1"],
    "market_gaps": ["市场空白1"],
    "opportunities": [
        {{
            "opportunity_name": "机会名称",
            "description": "描述",
            "market_potential": "市场潜力",
            "feasibility": "可行性",
            "competitive_advantage": "竞争优势",
            "investment_requirements": "投资需求"
        }}
    ],
    "recommended_priorities": ["推荐优先级1"],
    "implementation_timeline": "实施时间线",
    "risk_factors": ["风险因素1"]
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
                "focus_area": focus_area,
                "num_opportunities": num_opportunities,
                **result,
            }

        except Exception as e:
            logger.error(f"生成创新机会失败: {e}")
            return {
                "industry": industry,
                "focus_area": focus_area,
                "num_opportunities": num_opportunities,
                "executive_summary": "",
                "emerging_trends": [],
                "technology_insights": [],
                "market_gaps": [],
                "opportunities": [],
                "recommended_priorities": [],
                "implementation_timeline": "",
                "risk_factors": [],
            }


innovation_opportunity_generator_service = InnovationOpportunityGeneratorService()
