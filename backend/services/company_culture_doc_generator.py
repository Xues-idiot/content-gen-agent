"""
Vox Company Culture Doc Generator Service 模块

公司文化文档生成服务
- 价值观
- 行为准则
- 文化实践
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompanyCultureDocGeneratorService:
    """
    公司文化文档生成服务

    生成公司文化文档内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_company_culture_doc(
        self,
        company_name: str,
        company_stage: str,
        num_values: int = 5,
    ) -> Dict[str, Any]:
        """
        生成公司文化文档

        Args:
            company_name: 公司名称
            company_stage: 公司阶段
            num_values: 价值观数量

        Returns:
            Dict: 公司文化文档
        """
        try:
            prompt = f"""请为"{company_name}"（{company_stage}阶段）生成包含{num_values}个核心价值观的公司文化文档。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "company_stage": "公司阶段",
    "num_values": {num_values},
    "document_title": "文档标题",
    "mission_statement": "使命陈述",
    "vision_statement": "愿景陈述",
    "core_values": [
        {{
            "value": "价值观",
            "description": "描述",
            "behaviors": ["行为1"],
            "反例": "反例"
        }}
    ],
    "culture_pillars": ["文化支柱1"],
    "leadership_principles": ["领导原则1"],
    "communication_norms": ["沟通规范1"],
    "decision_making": "决策方式",
    "remote_work_policy": "远程办公政策",
    "meetings_hours": "会议时间",
    "recognition": "认可",
    "growth_development": "成长发展",
    "work_life_balance": "工作生活平衡",
    "onboarding_culture": "入职文化",
    "conflict_resolution": "冲突解决",
    "culture_fit_assessment": "文化契合评估"
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
                "company_stage": company_stage,
                "num_values": num_values,
                **result,
            }

        except Exception as e:
            logger.error(f"生成公司文化文档失败: {e}")
            return {
                "company_name": company_name,
                "company_stage": company_stage,
                "num_values": num_values,
                "document_title": "",
                "mission_statement": "",
                "vision_statement": "",
                "core_values": [],
                "culture_pillars": [],
                "leadership_principles": [],
                "communication_norms": [],
                "decision_making": "",
                "remote_work_policy": "",
                "meetings_hours": "",
                "recognition": "",
                "growth_development": "",
                "work_life_balance": "",
                "onboarding_culture": "",
                "conflict_resolution": "",
                "culture_fit_assessment": "",
            }


company_culture_doc_generator_service = CompanyCultureDocGeneratorService()