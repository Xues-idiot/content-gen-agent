"""
Vox One Pager Generator Service 模块

单页介绍生成服务
- 产品单页
- 服务概览
- 核心卖点
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class OnePagerGeneratorService:
    """
    单页介绍生成服务

    生成单页介绍内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_one_pager(
        self,
        product_name: str,
        product_type: str = "SaaS",
        target_customer: str = "中小企业",
    ) -> Dict[str, Any]:
        """
        生成单页介绍

        Args:
            product_name: 产品名称
            product_type: 产品类型
            target_customer: 目标客户

        Returns:
            Dict: 单页介绍
        """
        try:
            prompt = f"""请为"{product_name}"（类型：{product_type}，目标客户：{target_customer}）生成单页介绍。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "product_type": "产品类型",
    "target_customer": "目标客户",
    "tagline": "标语",
    "problem": "痛点问题",
    "solution": "解决方案",
    "key_features": ["核心功能1"],
    "benefits": ["好处1"],
    "use_cases": ["使用场景1"],
    "testimonial": "客户评价",
    "pricing_overview": "价格概览",
    "call_to_action": "行动号召"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "product_type": product_type,
                "target_customer": target_customer,
                **result,
            }

        except Exception as e:
            logger.error(f"生成单页介绍失败: {e}")
            return {
                "product_name": product_name,
                "product_type": product_type,
                "target_customer": target_customer,
                "tagline": "",
                "problem": "",
                "solution": "",
                "key_features": [],
                "benefits": [],
                "use_cases": [],
                "testimonial": "",
                "pricing_overview": "",
                "call_to_action": "",
            }


one_pager_generator_service = OnePagerGeneratorService()