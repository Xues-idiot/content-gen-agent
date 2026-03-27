"""
Vox Revenue Forecast Model Generator Service 模块

收入预测模型生成服务
- 预测变量
- 场景规划
- 趋势分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class RevenueForecastModelGeneratorService:
    """
    收入预测模型生成服务

    生成收入预测模型内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_revenue_forecast_model(
        self,
        business_unit: str,
        forecast_period: str,
        num_variables: int = 8,
    ) -> Dict[str, Any]:
        """
        生成收入预测模型

        Args:
            business_unit: 业务单元
            forecast_period: 预测周期
            num_variables: 变量数量

        Returns:
            Dict: 收入预测模型
        """
        try:
            prompt = f"""请为{business_unit}业务单元生成{forecast_period}的{num_variables}个变量的收入预测模型。

请以JSON格式返回：
{{
    "business_unit": "业务单元",
    "forecast_period": "预测周期",
    "num_variables": {num_variables},
    "model_methodology": "模型方法论",
    "key_variables": [
        {{
            "variable_name": "变量名称",
            "description": "描述",
            "data_source": "数据来源",
            "historical_correlation": "历史相关性"
        }}
    ],
    "forecast_assumptions": ["预测假设1"],
    "base_case_forecast": {{
        "revenue_projection": "收入预测",
        "confidence_interval": "置信区间",
        "growth_rate": "增长率"
    }},
    "scenario_analysis": [
        {{
            "scenario": "场景",
            "assumptions": ["假设1"],
            "revenue_impact": "收入影响"
        }}
    ],
    "seasonality_factors": "季节性因素",
    "validation_metrics": "验证指标",
    "model_limitations": "模型局限性"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "business_unit": business_unit,
                "forecast_period": forecast_period,
                "num_variables": num_variables,
                **result,
            }

        except Exception as e:
            logger.error(f"生成收入预测模型失败: {e}")
            return {
                "business_unit": business_unit,
                "forecast_period": forecast_period,
                "num_variables": num_variables,
                "model_methodology": "",
                "key_variables": [],
                "forecast_assumptions": [],
                "base_case_forecast": {},
                "scenario_analysis": [],
                "seasonality_factors": "",
                "validation_metrics": "",
                "model_limitations": "",
            }


revenue_forecast_model_generator_service = RevenueForecastModelGeneratorService()
