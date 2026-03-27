"""
Vox Executive Bio Generator Service 模块

高管简介生成服务
- 职业背景
- 成就亮点
- 媒体照片说明
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ExecutiveBioGeneratorService:
    """
    高管简介生成服务

    生成高管简介内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_executive_bio(
        self,
        executive_name: str,
        title: str,
        company: str,
        bio_type: str = "professional",
    ) -> Dict[str, Any]:
        """
        生成高管简介

        Args:
            executive_name: 高管姓名
            title: 职位
            company: 公司
            bio_type: 简介类型

        Returns:
            Dict: 高管简介
        """
        try:
            prompt = f"""请为"{executive_name}"（{title}，{company}）生成{bio_type}类型的高管简介。

请以JSON格式返回：
{{
    "executive_name": "高管姓名",
    "title": "职位",
    "company": "公司",
    "bio_type": "简介类型",
    "short_bio": "短简介（50字内）",
    "medium_bio": "中简介（100字内）",
    "long_bio": "长简介",
    "professional_background": "职业背景",
    "key_achievements": ["关键成就1"],
    "education": [
        {{
            "degree": "学位",
            "institution": "机构",
            "year": "年份"
        }}
    ],
    "board_positions": ["董事会职位1"],
    "industry_expertise": ["行业专业知识1"],
    "notable_recognition": ["著名奖项1"],
    "publications_speaking": ["出版物/演讲1"],
    "social_media_links": ["社交媒体链接1"],
    "headshot_photo_notes": "头像照片说明",
    "quotes": ["引言1"],
    "contact_info": "联系信息"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "executive_name": executive_name,
                "title": title,
                "company": company,
                "bio_type": bio_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成高管简介失败: {e}")
            return {
                "executive_name": executive_name,
                "title": title,
                "company": company,
                "bio_type": bio_type,
                "short_bio": "",
                "medium_bio": "",
                "long_bio": "",
                "professional_background": "",
                "key_achievements": [],
                "education": [],
                "board_positions": [],
                "industry_expertise": [],
                "notable_recognition": [],
                "publications_speaking": [],
                "social_media_links": [],
                "headshot_photo_notes": "",
                "quotes": [],
                "contact_info": "",
            }


executive_bio_generator_service = ExecutiveBioGeneratorService()