"""
Vox Media List Generator Service 模块

媒体名单生成服务
- 媒体联系人
- 记者信息
- 媒体偏好
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MediaListGeneratorService:
    """
    媒体名单生成服务

    生成媒体名单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_media_list(
        self,
        industry: str,
        outlet_types: List[str],
        region: str = "national",
    ) -> Dict[str, Any]:
        """
        生成媒体名单

        Args:
            industry: 行业
            outlet_types: 媒体类型
            region: 地区

        Returns:
            Dict: 媒体名单
        """
        try:
            types_str = ", ".join(outlet_types)
            prompt = f"""请为{industry}行业生成媒体名单（类型：{types_str}，地区：{region}）。

请以JSON格式返回：
{{
    "industry": "行业",
    "outlet_types": ["媒体类型1"],
    "region": "地区",
    "media_outlets": [
        {{
            "outlet_name": "媒体名称",
            "outlet_type": "媒体类型",
            "website": "网站",
            "audience_size": "受众规模",
            "coverage_focus": "报道重点"
        }}
    ],
    "journalists_bloggers": [
        {{
            "name": "姓名",
            "title": "职位",
            "outlet": "媒体",
            "beat": "报道领域",
            "email": "电子邮件",
            "twitter": "Twitter",
            "recent_coverage": ["近期报道1"]
        }}
    ],
    "editorial_calendars": [
        {{
            "outlet": "媒体",
            "issue_theme": "期刊主题",
            "deadline": "截止日期"
        }}
    ],
    "pitching_tips": ["推广技巧1"],
    "outreach_templates": ["外联模板1"],
    "media_preferences": {{
        "preferred_contact_method": "首选联系方式",
        "response_time": "响应时间",
        "exclusive_options": "独家选项"
    }},
    "tier_rankings": ["层级排名1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "industry": industry,
                "outlet_types": outlet_types,
                "region": region,
                **result,
            }

        except Exception as e:
            logger.error(f"生成媒体名单失败: {e}")
            return {
                "industry": industry,
                "outlet_types": outlet_types,
                "region": region,
                "media_outlets": [],
                "journalists_bloggers": [],
                "editorial_calendars": [],
                "pitching_tips": [],
                "outreach_templates": [],
                "media_preferences": {},
                "tier_rankings": [],
            }


media_list_generator_service = MediaListGeneratorService()