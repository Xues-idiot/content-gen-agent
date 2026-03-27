"""
Vox ROI Calculator Generator Service 模块

ROI计算器生成服务
- 计算公式
- 输入字段
- 结果展示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ROICalculatorGeneratorService:
    """
    ROI计算器生成服务

    生成ROI计算器内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_roi_calculator(
        self,
        product_service: str,
        num_inputs: int = 5,
        calculation_type: str = "annual",
    ) -> Dict[str, Any]:
        """
        生成ROI计算器

        Args:
            product_service: 产品/服务
            num_inputs: 输入字段数量
            calculation_type: 计算类型

        Returns:
            Dict: ROI计算器
        """
        try:
            prompt = f"""请为"{product_service}"生成{num_inputs}个输入字段的{calculation_type}类型ROI计算器。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "num_inputs": {num_inputs},
    "calculation_type": "计算类型",
    "calculator_title": "计算器标题",
    "input_fields": [
        {{
            "field_name": "字段名称",
            "field_label": "字段标签",
            "field_type": "字段类型",
            "default_value": "默认值",
            "helper_text": "帮助文本"
        }}
    ],
    "formula": "公式",
    "output_results": [
        {{
            "result_name": "结果名称",
            "result_format": "结果格式",
            "result_label": "结果标签"
        }}
    ],
    "assumptions": ["假设1"],
    "result_interpretation": "结果解释",
    "disclaimer": "免责声明"
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
                "num_inputs": num_inputs,
                "calculation_type": calculation_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成ROI计算器失败: {e}")
            return {
                "product_service": product_service,
                "num_inputs": num_inputs,
                "calculation_type": calculation_type,
                "calculator_title": "",
                "input_fields": [],
                "formula": "",
                "output_results": [],
                "assumptions": [],
                "result_interpretation": "",
                "disclaimer": "",
            }


roi_calculator_generator_service = ROICalculatorGeneratorService()