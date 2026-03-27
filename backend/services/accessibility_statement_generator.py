"""
Vox Accessibility Statement Generator Service 模块

无障碍声明生成服务
- 无障碍承诺
- 标准合规
- 支持信息
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AccessibilityStatementGeneratorService:
    """
    无障碍声明生成服务

    生成无障碍声明内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_accessibility_statement(
        self,
        website_name: str,
        organization_name: str,
        compliance_level: str = "WCAG 2.1 AA",
    ) -> Dict[str, Any]:
        """
        生成无障碍声明

        Args:
            website_name: 网站名称
            organization_name: 组织名称
            compliance_level: 合规级别

        Returns:
            Dict: 无障碍声明
        """
        try:
            prompt = f"""请为"{website_name}"（组织：{organization_name}，合规级别：{compliance_level}）生成无障碍声明。

请以JSON格式返回：
{{
    "website_name": "网站名称",
    "organization_name": "组织名称",
    "compliance_level": "合规级别",
    "effective_date": "生效日期",
    "commitment_statement": "承诺声明",
    "accessibility_features": ["无障碍功能1"],
    "accessibility_partial_conformance": ["部分符合1"],
    "non_accessible_content": ["非无障碍内容1"],
    "assessment_approach": "评估方法",
    "feedback_mechanism": "反馈机制",
    "contact_information": "联系信息",
    "enforcement_procedure": "执行程序",
    "technical_information": "技术信息",
    "compatible_browsers": "兼容浏览器",
    "assistive_technologies": "辅助技术",
    "training_materials": "培训材料"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "website_name": website_name,
                "organization_name": organization_name,
                "compliance_level": compliance_level,
                **result,
            }

        except Exception as e:
            logger.error(f"生成无障碍声明失败: {e}")
            return {
                "website_name": website_name,
                "organization_name": organization_name,
                "compliance_level": compliance_level,
                "effective_date": "",
                "commitment_statement": "",
                "accessibility_features": [],
                "accessibility_partial_conformance": [],
                "non_accessible_content": [],
                "assessment_approach": "",
                "feedback_mechanism": "",
                "contact_information": "",
                "enforcement_procedure": "",
                "technical_information": "",
                "compatible_browsers": "",
                "assistive_technologies": "",
                "training_materials": "",
            }


accessibility_statement_generator_service = AccessibilityStatementGeneratorService()