"""
Vox Interactive Calculator Generator Service 模块

互动计算器生成服务
- ROI计算
- 节省估算
- 定制化表单
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InteractiveCalculatorGeneratorService:
    """
    互动计算器生成服务

    生成互动计算器内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_interactive_calculator(
        self,
        calculator_type: str,
        target_audience: str,
        num_inputs: int = 5,
    ) -> Dict[str, Any]:
        """
        生成互动计算器

        Args:
            calculator_type: 计算器类型
            target_audience: 目标受众
            num_inputs: 输入字段数量

        Returns:
            Dict: 互动计算器
        """
        try:
            prompt = f"""请为{target_audience}生成{calculator_type}类型的互动计算器（{num_inputs}个输入字段）。

请以JSON格式返回：
{{
    "calculator_type": "计算器类型",
    "target_audience": "目标受众",
    "num_inputs": {num_inputs},
    "calculator_title": "计算器标题",
    "input_fields": [
        {{
            "field_name": "字段名称",
            "field_type": "字段类型",
            "label": "标签",
            "placeholder": "占位符",
            "default_value": "默认值"
        }}
    ],
    "formula_logic": "公式逻辑",
    "output_results": [
        {{
            "result_name": "结果名称",
            "result_format": "结果格式",
            "result_label": "结果标签"
        }}
    ],
    "assumptions": ["假设1"],
    "result_interpretation": "结果解释",
    "lead_capture_fields": ["潜在客户捕获字段1"],
    "sharing_options": ["分享选项1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "calculator_type": calculator_type,
                "target_audience": target_audience,
                "num_inputs": num_inputs,
                **result,
            }

        except Exception as e:
            logger.error(f"生成互动计算器失败: {e}")
            return {
                "calculator_type": calculator_type,
                "target_audience": target_audience,
                "num_inputs": num_inputs,
                "calculator_title": "",
                "input_fields": [],
                "formula_logic": "",
                "output_results": [],
                "assumptions": [],
                "result_interpretation": "",
                "lead_capture_fields": [],
                "sharing_options": [],
            }


interactive_calculator_generator_service = InteractiveCalculatorGeneratorService()