"""
Vox Client Checklist Generator Service 模块

客户检查清单生成服务
- 准备清单
- 需求收集
- 交付确认
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ClientChecklistGeneratorService:
    """
    客户检查清单生成服务

    生成客户检查清单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_client_checklist(
        self,
        project_type: str,
        checklist_purpose: str,
        num_items: int = 20,
    ) -> Dict[str, Any]:
        """
        生成客户检查清单

        Args:
            project_type: 项目类型
            checklist_purpose: 检查清单目的
            num_items: 项目数量

        Returns:
            Dict: 客户检查清单
        """
        try:
            prompt = f"""请为{project_type}项目生成{num_items}项的{cchecklist_purpose}客户检查清单。

请以JSON格式返回：
{{
    "project_type": "项目类型",
    "checklist_purpose": "检查清单目的",
    "num_items": {num_items},
    "checklist_title": "检查清单标题",
    "items": [
        {{
            "item_number": 1,
            "item": "项目",
            "description": "描述",
            "required": true,
            "category": "类别"
        }}
    ],
    "categories": ["类别1"],
    "timeline_recommendations": "时间线建议"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_type": project_type,
                "checklist_purpose": checklist_purpose,
                "num_items": num_items,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户检查清单失败: {e}")
            return {
                "project_type": project_type,
                "checklist_purpose": checklist_purpose,
                "num_items": num_items,
                "checklist_title": "",
                "items": [],
                "categories": [],
                "timeline_recommendations": "",
            }


client_checklist_generator_service = ClientChecklistGeneratorService()