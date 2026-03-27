"""
Vox Customer Persona Generator Service 模块

客户画像生成服务
- 用户画像
- 行为特征
- 需求分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerPersonaGeneratorService:
    """
    客户画像生成服务

    生成客户画像内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_persona(
        self,
        persona_name: str,
        demographic_info: str,
        industry: str = "",
    ) -> Dict[str, Any]:
        """
        生成客户画像

        Args:
            persona_name: 画像名称
            demographic_info: 人口统计信息
            industry: 行业

        Returns:
            Dict: 客户画像
        """
        try:
            industry_context = f"，行业：{industry}" if industry else ""
            prompt = f"""请为"{persona_name}"（{demographic_info}{industry_context}）生成客户画像。

请以JSON格式返回：
{{
    "persona_name": "画像名称",
    "demographic_info": "人口统计信息",
    "industry": "行业",
    "avatar": "头像描述",
    "background": "背景",
    "goals": ["目标1"],
    "pain_points": ["痛点1"],
    "motivations": ["动机1"],
    "behaviors": ["行为1"],
    "preferred_channels": ["偏好渠道1"],
    "content_preferences": ["内容偏好1"],
    "buying_patterns": "购买模式",
    "technology_usage": "技术使用",
    "quotes": ["引述1"],
    "success_metrics": "成功指标"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "persona_name": persona_name,
                "demographic_info": demographic_info,
                "industry": industry,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户画像失败: {e}")
            return {
                "persona_name": persona_name,
                "demographic_info": demographic_info,
                "industry": industry,
                "avatar": "",
                "background": "",
                "goals": [],
                "pain_points": [],
                "motivations": [],
                "behaviors": [],
                "preferred_channels": [],
                "content_preferences": [],
                "buying_patterns": "",
                "technology_usage": "",
                "quotes": [],
                "success_metrics": "",
            }


customer_persona_generator_service = CustomerPersonaGeneratorService()