"""
Vox Process Documentation Generator Service 模块

流程文档生成服务
- 业务流程
- 操作手册
- 流程图说明
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProcessDocumentationGeneratorService:
    """
    流程文档生成服务

    生成流程文档内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_process_documentation(
        self,
        process_name: str,
        department: str,
        complexity: str = "medium",
    ) -> Dict[str, Any]:
        """
        生成流程文档

        Args:
            process_name: 流程名称
            department: 部门
            complexity: 复杂程度

        Returns:
            Dict: 流程文档
        """
        try:
            prompt = f"""请为"{process_name}"流程（部门：{department}，复杂程度：{complexity}）生成文档。

请以JSON格式返回：
{{
    "process_name": "流程名称",
    "department": "部门",
    "complexity": "复杂程度",
    "overview": "流程概述",
    "purpose": "目的",
    "scope": "范围",
    "stakeholders": ["相关方1"],
    "prerequisites": ["前提条件1"],
    "steps": [
        {{
            "step_number": 1,
            "step_name": "步骤名称",
            "description": "描述",
            "responsible_party": "负责方",
            "tools_required": ["所需工具1"],
            "time_estimate": "时间估计"
        }}
    ],
    "decision_points": ["决策点1"],
    "error_handling": "错误处理",
    "metrics": ["指标1"],
    "related_processes": ["相关流程1"],
    "version": "版本"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "process_name": process_name,
                "department": department,
                "complexity": complexity,
                **result,
            }

        except Exception as e:
            logger.error(f"生成流程文档失败: {e}")
            return {
                "process_name": process_name,
                "department": department,
                "complexity": complexity,
                "overview": "",
                "purpose": "",
                "scope": "",
                "stakeholders": [],
                "prerequisites": [],
                "steps": [],
                "decision_points": [],
                "error_handling": "",
                "metrics": [],
                "related_processes": [],
                "version": "",
            }


process_documentation_generator_service = ProcessDocumentationGeneratorService()