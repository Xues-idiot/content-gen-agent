"""
Vox Client Brief Generator Service 模块

客户简报生成服务
- 项目概述
- 目标受众
- 交付要求
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ClientBriefGeneratorService:
    """
    客户简报生成服务

    生成客户简报内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_client_brief(
        self,
        project_name: str,
        client_name: str,
        project_type: str,
    ) -> Dict[str, Any]:
        """
        生成客户简报

        Args:
            project_name: 项目名称
            client_name: 客户名称
            project_type: 项目类型

        Returns:
            Dict: 客户简报
        """
        try:
            prompt = f"""请为"{project_name}"项目（客户：{client_name}，类型：{project_type}）生成客户简报。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "client_name": "客户名称",
    "project_type": "项目类型",
    "project_overview": "项目概述",
    "objectives": ["目标1"],
    "target_audience": {{
        "demographics": "人口统计",
        "psychographics": "心理统计",
        "behavior": "行为"
    }},
    "deliverables": ["交付物1"],
    "timeline": "时间线",
    "budget_range": "预算范围",
    "brand_guidelines": "品牌指南",
    "competitive_landscape": "竞争格局",
    "success_metrics": ["成功指标1"],
    "key_stakeholders": ["关键利益相关者1"],
    "challenges": ["挑战1"],
    "opportunities": ["机会1"],
    "tone_and_voice": "语气和语调",
    "mandatory_elements": ["必须元素1"],
    "restrictions": ["限制1"],
    "next_steps": "下一步"
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
                "project_type": project_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户简报失败: {e}")
            return {
                "project_name": project_name,
                "client_name": client_name,
                "project_type": project_type,
                "project_overview": "",
                "objectives": [],
                "target_audience": {},
                "deliverables": [],
                "timeline": "",
                "budget_range": "",
                "brand_guidelines": "",
                "competitive_landscape": "",
                "success_metrics": [],
                "key_stakeholders": [],
                "challenges": [],
                "opportunities": [],
                "tone_and_voice": "",
                "mandatory_elements": [],
                "restrictions": [],
                "next_steps": "",
            }


client_brief_generator_service = ClientBriefGeneratorService()