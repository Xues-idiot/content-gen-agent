"""
Vox Tradeshow Booth Content Generator Service 模块

展会展位内容生成服务
- 展位设计
- 宣传材料
- 互动内容
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TradeshowBoothContentGeneratorService:
    """
    展会展位内容生成服务

    生成展会展位内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_tradeshow_booth_content(
        self,
        event_name: str,
        company_name: str,
        booth_number: str,
    ) -> Dict[str, Any]:
        """
        生成展会展位内容

        Args:
            event_name: 展会名称
            company_name: 公司名称
            booth_number: 展位号

        Returns:
            Dict: 展会展位内容
        """
        try:
            prompt = f"""请为"{event_name}"展会的"{company_name}"（展位号：{booth_number}）生成展位内容。

请以JSON格式返回：
{{
    "event_name": "展会名称",
    "company_name": "公司名称",
    "booth_number": "展位号",
    "booth_theme": "展位主题",
    "key_messages": ["关键信息1"],
    "booth_layout_suggestions": "展位布局建议",
    "signage": {{
        "backdrop_text": "背景板文字",
        "side_panel_content": "侧板内容",
        "banner_messages": ["横幅信息1"]
    }},
    "printed_materials": [
        {{
            "material": "材料",
            "title": "标题",
            "description": "描述",
            "quantity": 数量
        }}
    ],
    "giveaways": [
        {{
            "item": "赠品",
            "branding": "品牌化",
            "quantity": 数量
        }}
    ],
    "interactive_elements": [
        {{
            "activity": "活动",
            "description": "描述",
            "engagement_goal": "参与目标"
        }}
    ],
    "staffing": {{
        "team_size": "团队规模",
        "roles": ["角色1"],
        "training_tips": ["培训提示1"]
    }},
    "lead_capture_questions": ["潜在客户捕获问题1"],
    "follow_up_email_template": "跟进邮件模板",
    "social_media_plan": "社交媒体计划",
    "budget_estimate": "预算估算",
    "checklist": ["检查清单1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "event_name": event_name,
                "company_name": company_name,
                "booth_number": booth_number,
                **result,
            }

        except Exception as e:
            logger.error(f"生成展会展位内容失败: {e}")
            return {
                "event_name": event_name,
                "company_name": company_name,
                "booth_number": booth_number,
                "booth_theme": "",
                "key_messages": [],
                "booth_layout_suggestions": "",
                "signage": {},
                "printed_materials": [],
                "giveaways": [],
                "interactive_elements": [],
                "staffing": {},
                "lead_capture_questions": [],
                "follow_up_email_template": "",
                "social_media_plan": "",
                "budget_estimate": "",
                "checklist": [],
            }


tradeshow_booth_content_generator_service = TradeshowBoothContentGeneratorService()