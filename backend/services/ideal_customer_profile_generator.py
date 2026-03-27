"""
Vox Ideal Customer Profile Generator Service 模块

理想客户画像生成服务
- 人口统计
- 行为特征
- 购买动机
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class IdealCustomerProfileGeneratorService:
    """
    理想客户画像生成服务

    生成理想客户画像内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_ideal_customer_profile(
        self,
        product_service: str,
        industry: str,
        num_attributes: int = 10,
    ) -> Dict[str, Any]:
        """
        生成理想客户画像

        Args:
            product_service: 产品/服务
            industry: 行业
            num_attributes: 属性数量

        Returns:
            Dict: 理想客户画像
        """
        try:
            prompt = f"""请为"{product_service}"生成{industry}行业的理想客户画像（{num_attributes}个属性）。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "industry": "行业",
    "num_attributes": {num_attributes},
    "profile_title": "画像标题",
    "demographic_attributes": {{
        "company_size": "公司规模",
        "industry_subsegment": "行业细分",
        "geography": "地理位置",
        "annual_revenue": "年收入"
    }},
    "firmographic_attributes": {{
        "company_stage": "公司阶段",
        "tech_savviness": "技术熟练度",
        "decision_makers": "决策者"
    }},
    "psychographic_attributes": {{
        "values": ["价值观1"],
        "attitudes": ["态度1"]
    }},
    "behavioral_attributes": {{
        "buying_behaviors": ["购买行为1"],
        "media_consumption": "媒体消费",
        "preferred_channels": ["首选渠道1"]
    }},
    "pain_points": ["痛点1"],
    "goals_aspirations": ["目标/愿望1"],
    "red_flags": ["红旗1"]
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
                "industry": industry,
                "num_attributes": num_attributes,
                **result,
            }

        except Exception as e:
            logger.error(f"生成理想客户画像失败: {e}")
            return {
                "product_service": product_service,
                "industry": industry,
                "num_attributes": num_attributes,
                "profile_title": "",
                "demographic_attributes": {},
                "firmographic_attributes": {},
                "psychographic_attributes": {},
                "behavioral_attributes": {},
                "pain_points": [],
                "goals_aspirations": [],
                "red_flags": [],
            }


ideal_customer_profile_generator_service = IdealCustomerProfileGeneratorService()