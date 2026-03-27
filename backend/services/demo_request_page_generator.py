"""
Vox Demo Request Page Generator Service 模块

演示请求页面生成服务
- 请求表单
- 价值预览
- 后续流程
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DemoRequestPageGeneratorService:
    """
    演示请求页面生成服务

    生成演示请求页面内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_demo_request_page(
        self,
        product_name: str,
        demo_type: str = "interactive",
        delivery_methods: List[str] = None,
    ) -> Dict[str, Any]:
        """
        生成演示请求页面

        Args:
            product_name: 产品名称
            demo_type: 演示类型
            delivery_methods: 交付方法列表

        Returns:
            Dict: 演示请求页面
        """
        if delivery_methods is None:
            delivery_methods = ["live", "recorded", "self-guided"]
        methods_str = ", ".join(delivery_methods)

        try:
            prompt = f"""请为"{product_name}"生成演示请求页面（类型：{demo_type}，交付方法：{methods_str}）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "demo_type": "演示类型",
    "delivery_methods": {delivery_methods},
    "page_headline": "页面标题",
    "hero_section": {{
        "headline": "标题",
        "subheadline": "副标题",
        "supporting_visuals": "支持视觉元素"
    }},
    "value_preview": {{
        "key_benefits": ["关键好处1"],
        "what_youll_see": ["你将看到的内容1"],
        "expected_outcomes": ["预期成果1"]
    }},
    "demo_options": [
        {{
            "option_name": "选项名称",
            "description": "描述",
            "duration": "时长",
            "best_for": "最适合"
        }}
    ],
    "form_fields": [
        {{
            "field_name": "字段名称",
            "field_type": "字段类型",
            "required": true,
            "placeholder": "占位符"
        }}
    ],
    "form_intro_text": "表单介绍文本",
    "submission_confirmation": "提交确认",
    "what_to_expect": "预期内容",
    "team_introduction": "团队介绍",
    "testimonials": ["推荐引言1"],
    "faq": [
        {{
            "question": "问题",
            "answer": "答案"
        }}
    ],
    "alternative_contact": "替代联系方式",
    "privacy_assurance": "隐私保证"
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
                "demo_type": demo_type,
                "delivery_methods": delivery_methods,
                **result,
            }

        except Exception as e:
            logger.error(f"生成演示请求页面失败: {e}")
            return {
                "product_name": product_name,
                "demo_type": demo_type,
                "delivery_methods": delivery_methods,
                "page_headline": "",
                "hero_section": {},
                "value_preview": {},
                "demo_options": [],
                "form_fields": [],
                "form_intro_text": "",
                "submission_confirmation": "",
                "what_to_expect": "",
                "team_introduction": "",
                "testimonials": [],
                "faq": [],
                "alternative_contact": "",
                "privacy_assurance": "",
            }


demo_request_page_generator_service = DemoRequestPageGeneratorService()