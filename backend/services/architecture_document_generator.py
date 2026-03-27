"""
Vox Architecture Document Generator Service 模块

架构文档生成服务
- 系统架构
- 组件设计
- 技术选型
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ArchitectureDocumentGeneratorService:
    """
    架构文档生成服务

    生成架构文档内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_architecture_document(
        self,
        system_name: str,
        system_type: str = "web application",
        num_components: int = 6,
    ) -> Dict[str, Any]:
        """
        生成架构文档

        Args:
            system_name: 系统名称
            system_type: 系统类型
            num_components: 组件数量

        Returns:
            Dict: 架构文档
        """
        try:
            prompt = f"""请为"{system_name}"（类型：{system_type}）生成包含{num_components}个组件的架构文档。

请以JSON格式返回：
{{
    "system_name": "系统名称",
    "system_type": "系统类型",
    "num_components": 组件数,
    "overview": "概述",
    "architecture_diagram_description": "架构图描述",
    "components": [
        {{
            "component_name": "组件名称",
            "description": "描述",
            "technology_stack": ["技术栈1"],
            "responsibilities": ["职责1"],
            "dependencies": ["依赖1"],
            "interfaces": ["接口1"]
        }}
    ],
    "data_flow": "数据流",
    "security_considerations": ["安全考虑1"],
    "scalability": "可扩展性",
    "monitoring_and_logging": "监控与日志",
    "disaster_recovery": "灾难恢复",
    "deployment_architecture": "部署架构",
    "technology_decisions": ["技术决策1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "system_name": system_name,
                "system_type": system_type,
                "num_components": num_components,
                **result,
            }

        except Exception as e:
            logger.error(f"生成架构文档失败: {e}")
            return {
                "system_name": system_name,
                "system_type": system_type,
                "num_components": num_components,
                "overview": "",
                "architecture_diagram_description": "",
                "components": [],
                "data_flow": "",
                "security_considerations": [],
                "scalability": "",
                "monitoring_and_logging": "",
                "disaster_recovery": "",
                "deployment_architecture": "",
                "technology_decisions": [],
            }


architecture_document_generator_service = ArchitectureDocumentGeneratorService()