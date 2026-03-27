"""
Vox Checklist Generator Service 模块

清单生成服务
- 任务清单
- 准备清单
- 检查事项
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ChecklistGeneratorService:
    """
    清单生成服务

    生成各类清单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_checklist(
        self,
        checklist_type: str,
        context: str,
        num_items: int = 10,
    ) -> Dict[str, Any]:
        """
        生成清单

        Args:
            checklist_type: 清单类型
            context: 使用场景
            num_items: 项目数量

        Returns:
            Dict: 清单
        """
        try:
            prompt = f"""请为"{context}"场景生成{num_items}项{checklist_type}清单。

请以JSON格式返回：
{{
    "checklist_type": "清单类型",
    "context": "使用场景",
    "num_items": 项目数量,
    "title": "清单标题",
    "items": [
        {{
            "item": "事项",
            "description": "说明",
            "priority": "优先级"
        }}
    ],
    "tips": ["小贴士1"],
    "common_mistakes": ["常见错误1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "checklist_type": checklist_type,
                "context": context,
                "num_items": num_items,
                **result,
            }

        except Exception as e:
            logger.error(f"生成清单失败: {e}")
            return {
                "checklist_type": checklist_type,
                "context": context,
                "num_items": num_items,
                "title": "",
                "items": [],
                "tips": [],
                "common_mistakes": [],
            }


checklist_generator_service = ChecklistGeneratorService()