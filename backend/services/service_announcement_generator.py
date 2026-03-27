"""
Vox Service Announcement Generator Service 模块

服务公告生成服务
- 服务变更
- 维护通知
- 新功能介绍
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ServiceAnnouncementGeneratorService:
    """
    服务公告生成服务

    生成服务公告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_service_announcement(
        self,
        announcement_type: str,
        service_name: str,
        effective_date: str,
    ) -> Dict[str, Any]:
        """
        生成服务公告

        Args:
            announcement_type: 公告类型
            service_name: 服务名称
            effective_date: 生效日期

        Returns:
            Dict: 服务公告
        """
        try:
            prompt = f"""请为"{service_name}"生成{announcement_type}类型（生效日期：{effective_date}）的服务公告。

请以JSON格式返回：
{{
    "announcement_type": "公告类型",
    "service_name": "服务名称",
    "effective_date": "生效日期",
    "announcement_title": "公告标题",
    "summary": "摘要",
    "details": "详情",
    "impact_on_customers": "对客户的影响",
    "actions_required": ["需要的行动1"],
    "timeline": "时间线",
    "support_information": "支持信息",
    "faq": ["常见问题1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "announcement_type": announcement_type,
                "service_name": service_name,
                "effective_date": effective_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成服务公告失败: {e}")
            return {
                "announcement_type": announcement_type,
                "service_name": service_name,
                "effective_date": effective_date,
                "announcement_title": "",
                "summary": "",
                "details": "",
                "impact_on_customers": "",
                "actions_required": [],
                "timeline": "",
                "support_information": "",
                "faq": [],
            }


service_announcement_generator_service = ServiceAnnouncementGeneratorService()