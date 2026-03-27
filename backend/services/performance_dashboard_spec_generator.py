"""
Vox Performance Dashboard Spec Generator Service 模块

绩效仪表板规范生成服务
- KPI定义
- 可视化设计
- 数据源
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PerformanceDashboardSpecGeneratorService:
    """
    绩效仪表板规范生成服务

    生成绩效仪表板规范内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_performance_dashboard_spec(
        self,
        dashboard_name: str,
        department: str,
        num_kpis: int = 10,
    ) -> Dict[str, Any]:
        """
        生成绩效仪表板规范

        Args:
            dashboard_name: 仪表板名称
            department: 部门
            num_kpis: KPI数量

        Returns:
            Dict: 绩效仪表板规范
        """
        try:
            prompt = f"""请为{department}部门生成{num_kpis}个KPI的"{dashboard_name}"仪表板规范。

请以JSON格式返回：
{{
    "dashboard_name": "仪表板名称",
    "department": "部门",
    "num_kpis": {num_kpis},
    "executive_summary": "执行摘要",
    "dashboard_objectives": "仪表板目标",
    "kpi_definitions": [
        {{
            "kpi_name": "KPI名称",
            "definition": "定义",
            "calculation": "计算",
            "data_source": "数据源",
            "update_frequency": "更新频率",
            "target_value": "目标值",
            "visualization_type": "可视化类型"
        }}
    ],
    "dashboard_layout": "仪表板布局",
    "filter_options": ["筛选选项1"],
    "user_roles_and_access": "用户角色和访问权限",
    "data_refresh_schedule": "数据刷新计划",
    "success_criteria": ["成功标准1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "dashboard_name": dashboard_name,
                "department": department,
                "num_kpis": num_kpis,
                **result,
            }

        except Exception as e:
            logger.error(f"生成绩效仪表板规范失败: {e}")
            return {
                "dashboard_name": dashboard_name,
                "department": department,
                "num_kpis": num_kpis,
                "executive_summary": "",
                "dashboard_objectives": "",
                "kpi_definitions": [],
                "dashboard_layout": "",
                "filter_options": [],
                "user_roles_and_access": "",
                "data_refresh_schedule": "",
                "success_criteria": [],
            }


performance_dashboard_spec_generator_service = PerformanceDashboardSpecGeneratorService()
