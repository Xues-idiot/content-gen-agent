"""
Vox Testimonial Collector Service 模块

客户感言收集服务
- 感言模板
- 收集引导
- 社交证明
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TestimonialCollectorService:
    """
    客户感言收集服务

    生成客户感言和收集引导
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_collection_request(
        self,
        product_name: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成感言收集请求

        Args:
            product_name: 产品名称
            platform: 平台

        Returns:
            Dict: 收集请求内容
        """
        try:
            prompt = f"""请为"{product_name}"生成一个客户感言收集请求。

平台：{platform}

请以JSON格式返回：
{{
    "request_message": "收集请求文案",
    "questions": ["问题1", "问题2"],
    "incentive": "激励措施"
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
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成感言收集请求失败: {e}")
            return {
                "product_name": product_name,
                "platform": platform,
                "request_message": "",
                "questions": [],
                "incentive": "",
            }


testimonial_collector_service = TestimonialCollectorService()