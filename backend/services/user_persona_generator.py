"""
Vox User Persona Generator Service 模块

用户画像生成服务
- 人口统计
- 行为模式
- 目标动机
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class UserPersonaGeneratorService:
    """
    用户画像生成服务

    生成用户画像内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_user_persona(
        self,
        product_service: str,
        persona_name: str,
    ) -> Dict[str, Any]:
        """
        生成用户画像

        Args:
            product_service: 产品/服务
            persona_name: 画像名称

        Returns:
            Dict: 用户画像
        """
        try:
            prompt = f"""请为"{product_service}"产品生成名为"{persona_name}"的用户画像。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "persona_name": "画像名称",
    "persona_summary": "画像摘要",
    "demographics": {{
        "age_range": "年龄范围",
        "gender": "性别",
        "location": "位置",
        "income_level": "收入水平",
        "education": "教育",
        "occupation": "职业"
    }},
    "professional_info": {{
        "job_title": "职位",
        "industry": "行业",
        "company_size": "公司规模",
        "years_of_experience": "工作年限"
    }},
    "goals_and_motivations": ["目标1"],
    "pain_points": ["痛点1"],
    "behavior_patterns": ["行为模式1"],
    "preferred_channels": ["首选渠道1"],
    "technology_usage": "技术使用",
    "decision_making_process": "决策过程",
    "quotes": ["引用1"],
    "persona_image_description": "画像图片描述"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_service": product_service,
                "persona_name": persona_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成用户画像失败: {e}")
            return {
                "product_service": product_service,
                "persona_name": persona_name,
                "persona_summary": "",
                "demographics": {},
                "professional_info": {},
                "goals_and_motivations": [],
                "pain_points": [],
                "behavior_patterns": [],
                "preferred_channels": [],
                "technology_usage": "",
                "decision_making_process": "",
                "quotes": [],
                "persona_image_description": "",
            }


user_persona_generator_service = UserPersonaGeneratorService()
