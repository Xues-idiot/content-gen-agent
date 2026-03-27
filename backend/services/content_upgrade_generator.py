"""
Vox Content Upgrade Generator Service 模块

内容升级生成服务
- Lead Magnet
- 升级类型
- 交付策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContentUpgradeGeneratorService:
    """
    内容升级生成服务

    生成内容升级内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_content_upgrade(
        self,
        content_topic: str,
        upgrade_type: str,
        target_audience: str,
    ) -> Dict[str, Any]:
        """
        生成内容升级

        Args:
            content_topic: 内容主题
            upgrade_type: 升级类型
            target_audience: 目标受众

        Returns:
            Dict: 内容升级
        """
        try:
            prompt = f"""请为"{content_topic}"生成针对{target_audience}的{upgrade_type}类型内容升级。

请以JSON格式返回：
{{
    "content_topic": "内容主题",
    "upgrade_type": "升级类型",
    "target_audience": "目标受众",
    "upgrade_title": "升级标题",
    "upgrade_description": "升级描述",
    "deliverable_details": {{
        "format": "格式",
        "length": "长度",
        "includes": ["包含内容1"]
    }},
    "cta_placement": "CTA放置",
    "cta_copy": "CTA文案",
    "delivery_method": "交付方式",
    "opt_in_form_fields": ["选择加入表单字段1"],
    "follow_up_sequence": "跟进序列"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "content_topic": content_topic,
                "upgrade_type": upgrade_type,
                "target_audience": target_audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成内容升级失败: {e}")
            return {
                "content_topic": content_topic,
                "upgrade_type": upgrade_type,
                "target_audience": target_audience,
                "upgrade_title": "",
                "upgrade_description": "",
                "deliverable_details": {},
                "cta_placement": "",
                "cta_copy": "",
                "delivery_method": "",
                "opt_in_form_fields": [],
                "follow_up_sequence": "",
            }


content_upgrade_generator_service = ContentUpgradeGeneratorService()