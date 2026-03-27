"""
Vox Product Showcase Generator Service 模块

产品展示生成服务
- 产品亮点
- 使用场景
- 客户案例
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductShowcaseGeneratorService:
    """
    产品展示生成服务

    生成产品展示内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_showcase(
        self,
        product_name: str,
        product_info: Dict[str, Any],
        showcase_type: str = "features",
    ) -> Dict[str, Any]:
        """
        生成产品展示

        Args:
            product_name: 产品名称
            product_info: 产品信息
            showcase_type: 展示类型

        Returns:
            Dict: 展示内容
        """
        try:
            prompt = f"""请为"{product_name}"生成一个产品展示。

类型：{showcase_type}
产品特点：{', '.join(product_info.get('selling_points', []))}

请以JSON格式返回：
{{
    "title": "展示标题",
    "highlights": ["亮点1", "亮点2"],
    "use_cases": ["场景1", "场景2"],
    "customer_story": "客户案例"
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
                "showcase_type": showcase_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品展示失败: {e}")
            return {
                "product_name": product_name,
                "showcase_type": showcase_type,
                "title": "",
                "highlights": [],
                "use_cases": [],
                "customer_story": "",
            }


product_showcase_generator_service = ProductShowcaseGeneratorService()