"""
Vox Territory Planning Generator Service 模块

区域规划生成服务
- 区域划分
- 目标设定
- 资源配置
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TerritoryPlanningGeneratorService:
    """
    区域规划生成服务

    生成区域规划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_territory_planning(
        self,
        region: str,
        sales_team_size: int,
        num_territories: int = 5,
    ) -> Dict[str, Any]:
        """
        生成区域规划

        Args:
            region: 区域
            sales_team_size: 销售团队规模
            num_territories: 区域数量

        Returns:
            Dict: 区域规划
        """
        try:
            prompt = f"""请为{region}区域生成{num_territories}个区域的销售区域规划（销售团队规模：{sales_team_size}人）。

请以JSON格式返回：
{{
    "region": "区域",
    "sales_team_size": {sales_team_size},
    "num_territories": {num_territories},
    "territories": [
        {{
            "territory_name": "区域名称",
            "assigned_reps": "分配的代表",
            "target_revenue": "目标收入",
            "key_accounts": ["关键账户1"],
            "market_potential": "市场潜力"
        }}
    ],
    "coverage_model": "覆盖模式",
    "territory_boundaries": "区域边界",
    "resource_allocation": "资源配置",
    "coordination_mechanism": "协调机制",
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
                "region": region,
                "sales_team_size": sales_team_size,
                "num_territories": num_territories,
                **result,
            }

        except Exception as e:
            logger.error(f"生成区域规划失败: {e}")
            return {
                "region": region,
                "sales_team_size": sales_team_size,
                "num_territories": num_territories,
                "territories": [],
                "coverage_model": "",
                "territory_boundaries": "",
                "resource_allocation": "",
                "coordination_mechanism": "",
                "success_metrics": [],
            }


territory_planning_generator_service = TerritoryPlanningGeneratorService()
