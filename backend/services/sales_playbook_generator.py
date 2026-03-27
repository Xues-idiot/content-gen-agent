"""
Vox Sales Playbook Generator Service 模块

销售手册生成服务
- 销售流程
- 对话脚本
- 异议处理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesPlaybookGeneratorService:
    """
    销售手册生成服务

    生成销售手册内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_playbook(
        self,
        product_service: str,
        target_segment: str,
        num_scenarios: int = 8,
    ) -> Dict[str, Any]:
        """
        生成销售手册

        Args:
            product_service: 产品/服务
            target_segment: 目标细分
            num_scenarios: 场景数量

        Returns:
            Dict: 销售手册
        """
        try:
            prompt = f"""请为"{product_service}"的{target_segment}细分市场生成{num_scenarios}个场景的销售手册。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "target_segment": "目标细分",
    "num_scenarios": {num_scenarios},
    "playbook_title": "手册标题",
    "sales_methodology": "销售方法论",
    "stages": [
        {{
            "stage_name": "阶段名称",
            "objectives": ["目标1"],
            "activities": ["活动1"],
            "scripts": ["话术1"],
            "duration": "持续时间"
        }}
    ],
    "scenario_guides": [
        {{
            "scenario": "场景",
            "approach": "方法",
            "key_talking_points": ["关键话题1"],
            "objection_handling": ["异议处理1"]
        }}
    ],
    "tools_templates": ["工具/模板1"],
    "success_metrics": ["成功指标1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_service": product_service,
                "target_segment": target_segment,
                "num_scenarios": num_scenarios,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售手册失败: {e}")
            return {
                "product_service": product_service,
                "target_segment": target_segment,
                "num_scenarios": num_scenarios,
                "playbook_title": "",
                "sales_methodology": "",
                "stages": [],
                "scenario_guides": [],
                "tools_templates": [],
                "success_metrics": [],
            }


sales_playbook_generator_service = SalesPlaybookGeneratorService()
