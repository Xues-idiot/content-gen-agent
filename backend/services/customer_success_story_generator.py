"""
Vox Customer Success Story Generator Service 模块

客户成功案例生成服务
- 转型故事
- 成果展示
- 推广引用
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerSuccessStoryGeneratorService:
    """
    客户成功案例生成服务

    生成客户成功案例内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_success_story(
        self,
        customer_name: str,
        product_service: str,
        industry: str,
    ) -> Dict[str, Any]:
        """
        生成客户成功案例

        Args:
            customer_name: 客户名称
            product_service: 产品/服务
            industry: 行业

        Returns:
            Dict: 客户成功案例
        """
        try:
            prompt = f"""请为"{customer_name}"生成{industry}行业的{product_service}客户成功案例。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "product_service": "产品/服务",
    "industry": "行业",
    "story_title": "故事标题",
    "executive_summary": "执行摘要",
    "customer_background": "客户背景",
    "challenge": "挑战",
    "solution": "解决方案",
    "implementation": "实施",
    "results_metrics": {{
        "before": "之前",
        "after": "之后",
        "improvement": "改善"
    }},
    "testimonial": {{
        "quote": "引言",
        "author": "作者",
        "title": "职位"
    }},
    "key_takeaways": ["关键收获1"],
    "quote_permissions": "引言许可"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "customer_name": customer_name,
                "product_service": product_service,
                "industry": industry,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户成功案例失败: {e}")
            return {
                "customer_name": customer_name,
                "product_service": product_service,
                "industry": industry,
                "story_title": "",
                "executive_summary": "",
                "customer_background": "",
                "challenge": "",
                "solution": "",
                "implementation": "",
                "results_metrics": {},
                "testimonial": {},
                "key_takeaways": [],
                "quote_permissions": "",
            }


customer_success_story_generator_service = CustomerSuccessStoryGeneratorService()