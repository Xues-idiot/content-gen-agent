"""
Vox Service Catalog Generator Service 模块

服务目录生成服务
- 服务列表
- 服务描述
- 定价方案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ServiceCatalogGeneratorService:
    """
    服务目录生成服务

    生成服务目录内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_service_catalog(
        self,
        company_name: str,
        industry: str,
        num_services: int = 8,
    ) -> Dict[str, Any]:
        """
        生成服务目录

        Args:
            company_name: 公司名称
            industry: 行业
            num_services: 服务数量

        Returns:
            Dict: 服务目录
        """
        try:
            prompt = f"""请为"{company_name}"（{industry}行业）生成包含{num_services}项服务的目录。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "industry": "行业",
    "catalog_title": "目录标题",
    "introduction": "简介",
    "services": [
        {{
            "service_name": "服务名称",
            "category": "类别",
            "description": "描述",
            "features": ["功能1"],
            "pricing_model": "定价模式",
            "delivery_time": "交付时间"
        }}
    ],
    "process_overview": "流程概述",
    "why_choose_us": "选择我们的理由",
    "contact_information": "联系方式"
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
                "num_services": num_services,
                **result,
            }

        except Exception as e:
            logger.error(f"生成服务目录失败: {e}")
            return {
                "company_name": company_name,
                "industry": industry,
                "num_services": num_services,
                "catalog_title": "",
                "introduction": "",
                "services": [],
                "process_overview": "",
                "why_choose_us": "",
                "contact_information": "",
            }


service_catalog_generator_service = ServiceCatalogGeneratorService()