"""
Vox Product Announcement Generator Service 模块

产品公告生成服务
- 新品发布
- 功能更新
- 版本说明
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductAnnouncementGeneratorService:
    """
    产品公告生成服务

    生成产品公告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_announcement(
        self,
        product_name: str,
        announcement_type: str,
        version: str = "1.0",
    ) -> Dict[str, Any]:
        """
        生成产品公告

        Args:
            product_name: 产品名称
            announcement_type: 公告类型
            version: 版本号

        Returns:
            Dict: 产品公告
        """
        try:
            prompt = f"""请为"{product_name}"{version}版本生成{announcement_type}公告。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "announcement_type": "公告类型",
    "version": "版本号",
    "headline": "标题",
    "subheadline": "副标题",
    "announcement_body": "公告正文",
    "key_highlights": ["亮点1"],
    "new_features": ["新功能1"],
    "improvements": ["改进1"],
    "bug_fixes": ["修复1"],
    "availability": "可用性",
    "upgrade_notice": "升级通知",
    "screenshots": ["截图建议"],
    "download_link": "下载链接",
    "contact_info": "联系方式"
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
                "announcement_type": announcement_type,
                "version": version,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品公告失败: {e}")
            return {
                "product_name": product_name,
                "announcement_type": announcement_type,
                "version": version,
                "headline": "",
                "subheadline": "",
                "announcement_body": "",
                "key_highlights": [],
                "new_features": [],
                "improvements": [],
                "bug_fixes": [],
                "availability": "",
                "upgrade_notice": "",
                "screenshots": [],
                "download_link": "",
                "contact_info": "",
            }


product_announcement_generator_service = ProductAnnouncementGeneratorService()