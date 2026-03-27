"""
Vox Technology Stack Assessment Generator Service 模块

技术栈评估生成服务
- 技术成熟度
- 集成分析
- 现代化建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TechnologyStackAssessmentGeneratorService:
    """
    技术栈评估生成服务

    生成技术栈评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_technology_stack_assessment(
        self,
        organization: str,
        assessment_scope: str,
        num_technologies: int = 10,
    ) -> Dict[str, Any]:
        """
        生成技术栈评估

        Args:
            organization: 组织
            assessment_scope: 评估范围
            num_technologies: 技术数量

        Returns:
            Dict: 技术栈评估
        """
        try:
            prompt = f"""请为{organization}的{assessment_scope}范围生成{num_technologies}个技术的评估。

请以JSON格式返回：
{{
    "organization": "组织",
    "assessment_scope": "评估范围",
    "num_technologies": {num_technologies},
    "executive_summary": "执行摘要",
    "technology_assessment": [
        {{
            "technology_name": "技术名称",
            "current_version": "当前版本",
            "maturity_level": "成熟度级别",
            "performance_rating": "性能评级",
            "security_rating": "安全评级",
            "maintenance_effort": "维护工作量",
            "integration_complexity": "集成复杂度"
        }}
    ],
    "technical_debt": "技术债务",
    "integration_gaps": "集成差距",
    "modernization_opportunities": ["现代化机会1"],
    "risk_assessment": ["风险评估1"],
    "recommended_actions": ["推荐行动1"],
    "investment_requirements": "投资需求"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "organization": organization,
                "assessment_scope": assessment_scope,
                "num_technologies": num_technologies,
                **result,
            }

        except Exception as e:
            logger.error(f"生成技术栈评估失败: {e}")
            return {
                "organization": organization,
                "assessment_scope": assessment_scope,
                "num_technologies": num_technologies,
                "executive_summary": "",
                "technology_assessment": [],
                "technical_debt": "",
                "integration_gaps": "",
                "modernization_opportunities": [],
                "risk_assessment": [],
                "recommended_actions": [],
                "investment_requirements": "",
            }


technology_stack_assessment_generator_service = TechnologyStackAssessmentGeneratorService()
