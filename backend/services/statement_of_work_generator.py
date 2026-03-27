"""
Vox Statement Of Work Generator Service 模块

工作说明书生成服务
- 项目范围
- 交付物
- 时间线
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class StatementOfWorkGeneratorService:
    """
    工作说明书生成服务

    生成工作说明书内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_statement_of_work(
        self,
        project_name: str,
        client_name: str,
        project_duration: str,
    ) -> Dict[str, Any]:
        """
        生成工作说明书

        Args:
            project_name: 项目名称
            client_name: 客户名称
            project_duration: 项目持续时间

        Returns:
            Dict: 工作说明书
        """
        try:
            prompt = f"""请为"{project_name}"（客户：{client_name}，持续时间：{project_duration}）生成工作说明书。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "client_name": "客户名称",
    "project_duration": "项目持续时间",
    "document_version": "文档版本",
    "effective_date": "生效日期",
    "project_overview": "项目概述",
    "scope_of_work": {{
        "in_scope": ["范围内的内容1"],
        "out_of_scope": ["范围外的内容1"]
    }},
    "deliverables": [
        {{
            "deliverable": "交付物",
            "description": "描述",
            "due_date": "截止日期",
            "acceptance_criteria": "验收标准"
        }}
    ],
    "timeline": "时间线",
    "assumptions": ["假设1"],
    "dependencies": ["依赖1"],
    "change_management": "变更管理",
    "payment_terms": "付款条款",
    "signature_block": "签名栏"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_name": project_name,
                "client_name": client_name,
                "project_duration": project_duration,
                **result,
            }

        except Exception as e:
            logger.error(f"生成工作说明书失败: {e}")
            return {
                "project_name": project_name,
                "client_name": client_name,
                "project_duration": project_duration,
                "document_version": "",
                "effective_date": "",
                "project_overview": "",
                "scope_of_work": {},
                "deliverables": [],
                "timeline": "",
                "assumptions": [],
                "dependencies": [],
                "change_management": "",
                "payment_terms": "",
                "signature_block": "",
            }


statement_of_work_generator_service = StatementOfWorkGeneratorService()