"""
Vox Product Roadmap Generator Service 模块

产品路线图生成服务
- 版本规划
- 功能路线
- 开发计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductRoadmapGeneratorService:
    """
    产品路线图生成服务

    生成产品路线图内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_roadmap(
        self,
        product_name: str,
        planning_period: str = "12 months",
        num_versions: int = 4,
    ) -> Dict[str, Any]:
        """
        生成产品路线图

        Args:
            product_name: 产品名称
            planning_period: 规划周期
            num_versions: 版本数量

        Returns:
            Dict: 产品路线图
        """
        try:
            prompt = f"""请为"{product_name}"生成{planning_period}产品路线图（{num_versions}个版本）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "planning_period": "规划周期",
    "num_versions": 版本数量,
    "overview": "概述",
    "versions": [
        {{
            "version": "版本号",
            "release_date": "发布日期",
            "codename": "代号",
            "theme": "主题",
            "features": ["功能1"],
            "improvements": ["改进1"],
            "bug_fixes": ["修复1"],
            "milestones": ["里程碑1"]
        }}
    ],
    "technical_requirements": ["技术需求1"],
    "resource_needs": "资源需求",
    "risks_and_mitigations": ["风险与缓解1"],
    "success_metrics": "成功指标"
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
                "planning_period": planning_period,
                "num_versions": num_versions,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品路线图失败: {e}")
            return {
                "product_name": product_name,
                "planning_period": planning_period,
                "num_versions": num_versions,
                "overview": "",
                "versions": [],
                "technical_requirements": [],
                "resource_needs": "",
                "risks_and_mitigations": [],
                "success_metrics": "",
            }


product_roadmap_generator_service = ProductRoadmapGeneratorService()