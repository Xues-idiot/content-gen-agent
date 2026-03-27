"""
Vox Press Kit Generator Service 模块

媒体资料包生成服务
- 新闻通稿
- 品牌资料
- 媒体联系
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PressKitGeneratorService:
    """
    媒体资料包生成服务

    生成媒体资料包内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_press_kit(
        self,
        company_name: str,
        industry: str,
        launch_date: str = "TBD",
    ) -> Dict[str, Any]:
        """
        生成媒体资料包

        Args:
            company_name: 公司名称
            industry: 行业
            launch_date: 发布日期

        Returns:
            Dict: 媒体资料包
        """
        try:
            prompt = f"""请为"{company_name}"（{industry}行业）生成媒体资料包，发布/活动日期：{launch_date}。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "industry": "行业",
    "launch_date": "发布日期",
    "press_release": "新闻通稿",
    "company_backgrounder": "公司背景资料",
    "key_messages": ["关键信息1"],
    "leadership_bios": ["高管简介1"],
    "product_service_descriptions": ["产品/服务描述1"],
    "mediaAssets": ["媒体资产1"],
    "awards_and_recognition": ["获奖与认可1"],
    "contact_information": {{
        "media_contact_name": "媒体联系人",
        "email": "邮箱",
        "phone": "电话"
    }},
    "social_media_handles": ["社交媒体账号1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_name": company_name,
                "industry": industry,
                "launch_date": launch_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成媒体资料包失败: {e}")
            return {
                "company_name": company_name,
                "industry": industry,
                "launch_date": launch_date,
                "press_release": "",
                "company_backgrounder": "",
                "key_messages": [],
                "leadership_bios": [],
                "product_service_descriptions": [],
                "mediaAssets": [],
                "awards_and_recognition": [],
                "contact_information": {},
                "social_media_handles": [],
            }


press_kit_generator_service = PressKitGeneratorService()