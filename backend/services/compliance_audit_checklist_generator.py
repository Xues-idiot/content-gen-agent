"""
Vox Compliance Audit Checklist Generator Service 模块

合规审计检查清单生成服务
- 审计领域
- 检查点
- 文档要求
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ComplianceAuditChecklistGeneratorService:
    """
    合规审计检查清单生成服务

    生成合规审计检查清单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_compliance_audit_checklist(
        self,
        regulation_name: str,
        organization_type: str,
        num_areas: int = 10,
    ) -> Dict[str, Any]:
        """
        生成合规审计检查清单

        Args:
            regulation_name: 法规名称
            organization_type: 组织类型
            num_areas: 领域数量

        Returns:
            Dict: 合规审计检查清单
        """
        try:
            prompt = f"""请为{regulation_name}法规生成适用于{organization_type}类型的{num_areas}个领域的合规审计检查清单。

请以JSON格式返回：
{{
    "regulation_name": "法规名称",
    "organization_type": "组织类型",
    "num_areas": {num_areas},
    "executive_summary": "执行摘要",
    "audit_areas": [
        {{
            "area_name": "领域名称",
            "audit_objectives": ["审计目标1"],
            "checkpoints": ["检查点1"],
            "required_evidence": ["所需证据1"],
            "common_findings": ["常见发现1"]
        }}
    ],
    "evidence_requirements": ["证据要求1"],
    "interview_questions": ["访谈问题1"],
    "documentation_checklist": ["文档检查清单1"],
    "scoring_methodology": "评分方法",
    "remediation_timeline": "补救时间线",
    "follow_up_procedures": "跟进程序"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "regulation_name": regulation_name,
                "organization_type": organization_type,
                "num_areas": num_areas,
                **result,
            }

        except Exception as e:
            logger.error(f"生成合规审计检查清单失败: {e}")
            return {
                "regulation_name": regulation_name,
                "organization_type": organization_type,
                "num_areas": num_areas,
                "executive_summary": "",
                "audit_areas": [],
                "evidence_requirements": [],
                "interview_questions": [],
                "documentation_checklist": [],
                "scoring_methodology": "",
                "remediation_timeline": "",
                "follow_up_procedures": "",
            }


compliance_audit_checklist_generator_service = ComplianceAuditChecklistGeneratorService()
