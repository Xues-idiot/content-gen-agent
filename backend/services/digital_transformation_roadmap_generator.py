"""
Vox Digital Transformation Roadmap Generator Service 模块

数字化转型路线图生成服务
- 转型阶段
- 技术投资
- 变革管理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DigitalTransformationRoadmapGeneratorService:
    """
    数字化转型路线图生成服务

    生成数字化转型路线图内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_digital_transformation_roadmap(
        self,
        organization: str,
        transformation_scope: str,
        num_phases: int = 4,
    ) -> Dict[str, Any]:
        """
        生成数字化转型路线图

        Args:
            organization: 组织
            transformation_scope: 转型范围
            num_phases: 阶段数量

        Returns:
            Dict: 数字化转型路线图
        """
        try:
            prompt = f"""请为{organization}生成{transformation_scope}范围的{num_phases}阶段数字化转型路线图。

请以JSON格式返回：
{{
    "organization": "组织",
    "transformation_scope": "转型范围",
    "num_phases": {num_phases},
    "executive_summary": "执行摘要",
    "transformation_vision": "转型愿景",
    "phases": [
        {{
            "phase_name": "阶段名称",
            "duration": "持续时间",
            "key_objectives": ["关键目标1"],
            "technology_initiatives": ["技术举措1"],
            "expected_outcomes": ["预期成果1"]
        }}
    ],
    "technology_investments": ["技术投资1"],
    "change_management_plan": "变革管理计划",
    "skill_development": "技能发展",
    "risk_mitigation": "风险缓解",
    "success_metrics": ["成功指标1"],
    "budget_requirements": "预算需求"
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
                "transformation_scope": transformation_scope,
                "num_phases": num_phases,
                **result,
            }

        except Exception as e:
            logger.error(f"生成数字化转型路线图失败: {e}")
            return {
                "organization": organization,
                "transformation_scope": transformation_scope,
                "num_phases": num_phases,
                "executive_summary": "",
                "transformation_vision": "",
                "phases": [],
                "technology_investments": [],
                "change_management_plan": "",
                "skill_development": "",
                "risk_mitigation": "",
                "success_metrics": [],
                "budget_requirements": "",
            }


digital_transformation_roadmap_generator_service = DigitalTransformationRoadmapGeneratorService()
