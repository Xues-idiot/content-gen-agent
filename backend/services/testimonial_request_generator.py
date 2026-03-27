"""
Vox Testimonial Request Generator Service 模块

推荐信请求生成服务
- 请求模板
- 提问设计
- 收集流程
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TestimonialRequestGeneratorService:
    """
    推荐信请求生成服务

    生成推荐信请求内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_testimonial_request(
        self,
        customer_name: str,
        product_name: str,
        relationship: str = "客户",
    ) -> Dict[str, Any]:
        """
        生成推荐信请求

        Args:
            customer_name: 客户名称
            product_name: 产品名称
            relationship: 关系

        Returns:
            Dict: 推荐信请求
        """
        try:
            prompt = f"""请为"{customer_name}"（{product_name}的{relationship}）生成推荐信请求。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "product_name": "产品名称",
    "relationship": "关系",
    "request_subject": "请求主题",
    "request_message": "请求信息",
    "guidelines": ["指导原则1"],
    "suggested_questions": [
        {{
            "question": "问题",
            "purpose": "目的"
        }}
    ],
    "testimonial_format_options": ["格式选项1"],
    "permission_text": "授权文字",
    "follow_up_timeline": "跟进时间",
    "thank_you_message": "感谢信息"
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
                "product_name": product_name,
                "relationship": relationship,
                **result,
            }

        except Exception as e:
            logger.error(f"生成推荐信请求失败: {e}")
            return {
                "customer_name": customer_name,
                "product_name": product_name,
                "relationship": relationship,
                "request_subject": "",
                "request_message": "",
                "guidelines": [],
                "suggested_questions": [],
                "testimonial_format_options": [],
                "permission_text": "",
                "follow_up_timeline": "",
                "thank_you_message": "",
            }


testimonial_request_generator_service = TestimonialRequestGeneratorService()