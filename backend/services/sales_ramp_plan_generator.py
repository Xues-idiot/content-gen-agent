"""
Vox Sales Ramp Plan Generator Service 模块

销售 ramping 计划生成服务
- 新人培训
- 目标设定
- 成长期望
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesRampPlanGeneratorService:
    """
    销售 ramping 计划生成服务

    生成销售 ramping 计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_ramp_plan(
        self,
        sales_rep_name: str,
        territory: str,
        ramp_period: str = "90 days",
    ) -> Dict[str, Any]:
        """
        生成销售 ramping 计划

        Args:
            sales_rep_name: 销售代表姓名
            territory: 区域
            ramp_period: ramping 周期

        Returns:
            Dict: 销售 ramping 计划
        """
        try:
            prompt = f"""请为销售代表"{sales_rep_name}"生成{territory}区域的{ramp_period}销售 ramping 计划。

请以JSON格式返回：
{{
    "sales_rep_name": "销售代表姓名",
    "territory": "区域",
    "ramp_period": "ramping周期",
    "start_date": "开始日期",
    "end_date": "结束日期",
    "phases": [
        {{
            "phase_name": "阶段名称",
            "duration": "持续时间",
            "objectives": ["目标1"],
            "training_requirements": ["培训要求1"],
            "expected_output": "预期产出"
        }}
    ],
    "monthly_targets": [
        {{
            "month": "月份",
            "revenue_target": "收入目标",
            "activities": ["活动1"]
        }}
    ],
    "key_milestones": ["关键里程碑1"],
    "mentorship_plan": "导师计划",
    "success_criteria": ["成功标准1"],
    "support_resources": ["支持资源1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "sales_rep_name": sales_rep_name,
                "territory": territory,
                "ramp_period": ramp_period,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售 ramping 计划失败: {e}")
            return {
                "sales_rep_name": sales_rep_name,
                "territory": territory,
                "ramp_period": ramp_period,
                "start_date": "",
                "end_date": "",
                "phases": [],
                "monthly_targets": [],
                "key_milestones": [],
                "mentorship_plan": "",
                "success_criteria": [],
                "support_resources": [],
            }


sales_ramp_plan_generator_service = SalesRampPlanGeneratorService()
