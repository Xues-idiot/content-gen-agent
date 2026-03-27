"""
Vox DM Template Generator Service 模块

私信模板生成服务
- 外联私信
- 合作洽谈
- KOL联系
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DMTemplateGeneratorService:
    """
    私信模板生成服务

    生成各种场景的私信模板
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_dm_template(
        self,
        dm_type: str = "outreach",
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成私信模板

        Args:
            dm_type: 私信类型
            platform: 平台

        Returns:
            Dict: 私信模板
        """
        try:
            prompt = f"""请为{platform}平台生成一条{dm_type}类型的私信模板。

请以JSON格式返回：
{{
    "subject": "主题（可选）",
    "body": "私信正文",
    "tips": ["撰写技巧1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "dm_type": dm_type,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成私信模板失败: {e}")
            return {
                "dm_type": dm_type,
                "platform": platform,
                "subject": "",
                "body": "",
                "tips": [],
            }


dm_template_generator_service = DMTemplateGeneratorService()