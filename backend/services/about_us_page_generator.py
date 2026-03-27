"""
Vox About Us Page Generator Service 模块

关于我们页面生成服务
- 公司故事
- 团队介绍
- 使命愿景
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AboutUsPageGeneratorService:
    """
    关于我们页面生成服务

    生成关于我们页面内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_about_us_page(
        self,
        company_name: str,
        page_type: str = "standard",
        company_age_years: int = 10,
    ) -> Dict[str, Any]:
        """
        生成关于我们页面

        Args:
            company_name: 公司名称
            page_type: 页面类型
            company_age_years: 公司年龄（年）

        Returns:
            Dict: 关于我们页面
        """
        try:
            prompt = f"""请为"{company_name}"（成立{company_age_years}年）生成{page_type}类型的关于我们页面。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "page_type": "页面类型",
    "hero_section": {{
        "headline": "标题",
        "subheadline": "副标题",
        "background_story_hook": "背景故事钩子"
    }},
    "our_story": {{
        "founding_story": "创立故事",
        "evolution": "发展历程",
        "key_milestones": ["关键里程碑1"]
    }},
    "mission_values": {{
        "mission": "使命",
        "vision": "愿景",
        "core_values": ["核心价值观1"],
        "purpose": "宗旨"
    }},
    "leadership_team": [
        {{
            "name": "姓名",
            "title": "职位",
            "bio": "简介",
            "photo_description": "照片描述"
        }}
    ],
    "company_culture": {{
        "work_environment": "工作环境",
        "team_dynamics": "团队活力",
        "diversity_inclusion": "多元化与包容"
    }},
    "achievements_awards": ["成就/奖项1"],
    "community_involvement": "社区参与",
    "partnerships": ["合作伙伴1"],
    "company_facts": {{
        "founded": "成立时间",
        "headquarters": "总部",
        "employees": "员工数",
        "locations": ["地点1"],
        "customers": "客户数"
    }},
    "testimonial_quote": "推荐引言",
    "contact_information": "联系信息",
    "cta_section": "CTA部分"
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
                "page_type": page_type,
                "company_age_years": company_age_years,
                **result,
            }

        except Exception as e:
            logger.error(f"生成关于我们页面失败: {e}")
            return {
                "company_name": company_name,
                "page_type": page_type,
                "company_age_years": company_age_years,
                "hero_section": {},
                "our_story": {},
                "mission_values": {},
                "leadership_team": [],
                "company_culture": {},
                "achievements_awards": [],
                "community_involvement": "",
                "partnerships": [],
                "company_facts": {},
                "testimonial_quote": "",
                "contact_information": "",
                "cta_section": "",
            }


about_us_page_generator_service = AboutUsPageGeneratorService()