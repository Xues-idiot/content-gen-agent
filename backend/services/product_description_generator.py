"""
Vox Product Description Generator Service 模块

产品描述生成服务
- 产品特点
- 使用场景
- 规格参数
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductDescriptionGeneratorService:
    """
    产品描述生成服务

    生成产品描述内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_description(
        self,
        product_name: str,
        category: str,
        target_audience: str,
    ) -> Dict[str, Any]:
        """
        生成产品描述

        Args:
            product_name: 产品名称
            category: 产品类别
            target_audience: 目标受众

        Returns:
            Dict: 产品描述
        """
        try:
            prompt = f"""请为"{product_name}"（类别：{category}，目标受众：{target_audience}）生成产品描述。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "short_description": "简短描述",
    "key_features": ["特点1", "特点2"],
    "specifications": ["规格1"],
    "use_cases": ["使用场景1"],
    "benefits": ["好处1"],
    "packaging_info": "包装信息"
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
                "category": category,
                "target_audience": target_audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品描述失败: {e}")
            return {
                "product_name": product_name,
                "category": category,
                "target_audience": target_audience,
                "short_description": "",
                "key_features": [],
                "specifications": [],
                "use_cases": [],
                "benefits": [],
                "packaging_info": "",
            }


product_description_generator_service = ProductDescriptionGeneratorService()