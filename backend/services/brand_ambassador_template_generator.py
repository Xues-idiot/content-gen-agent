"""
Vox Brand Ambassador Template Generator Service 模块

品牌大使模板生成服务
- 合作协议
- 内容指南
- 绩效追踪
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandAmbassadorTemplateGeneratorService:
    """
    品牌大使模板生成服务

    生成品牌大使模板内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_brand_ambassador_template(
        self,
        brand_name: str,
        program_duration: str,
        ambassador_tier: str = "standard",
    ) -> Dict[str, Any]:
        """
        生成品牌大使模板

        Args:
            brand_name: 品牌名称
            program_duration: 项目持续时间
            ambassador_tier: 大使层级

        Returns:
            Dict: 品牌大使模板
        """
        try:
            prompt = f"""请为"{brand_name}"生成{ambassador_tier}层级的{program_duration}品牌大使项目模板。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "program_duration": "项目持续时间",
    "ambassador_tier": "大使层级",
    "agreement_template": "协议模板",
    "program_overview": "项目概述",
    "benefits_perks": ["福利/待遇1"],
    "responsibilities": ["职责1"],
    "content_guidelines": "内容指南",
    "posting_requirements": "发布要求",
    "performance_expectations": "绩效期望",
    "compensation_structure": "薪酬结构",
    "code_of_conduct": "行为准则",
    "brand_assets_access": "品牌资产访问",
    "reporting_requirements": "报告要求",
    "termination_clause": "终止条款"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_name": brand_name,
                "program_duration": program_duration,
                "ambassador_tier": ambassador_tier,
                **result,
            }

        except Exception as e:
            logger.error(f"生成品牌大使模板失败: {e}")
            return {
                "brand_name": brand_name,
                "program_duration": program_duration,
                "ambassador_tier": ambassador_tier,
                "agreement_template": "",
                "program_overview": "",
                "benefits_perks": [],
                "responsibilities": [],
                "content_guidelines": "",
                "posting_requirements": "",
                "performance_expectations": "",
                "compensation_structure": "",
                "code_of_conduct": "",
                "brand_assets_access": "",
                "reporting_requirements": "",
                "termination_clause": "",
            }


brand_ambassador_template_generator_service = BrandAmbassadorTemplateGeneratorService()