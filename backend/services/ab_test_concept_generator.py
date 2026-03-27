"""
Vox A/B Test Concept Generator Service 模块

A/B测试概念生成服务
- 测试假设
- 变量设计
- 成功标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ABTestConceptGeneratorService:
    """
    A/B测试概念生成服务

    生成A/B测试概念内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_ab_test_concept(
        self,
        page_element: str,
        test_goal: str,
        traffic_volume: str = "medium",
    ) -> Dict[str, Any]:
        """
        生成A/B测试概念

        Args:
            page_element: 页面元素
            test_goal: 测试目标
            traffic_volume: 流量规模

        Returns:
            Dict: A/B测试概念
        """
        try:
            prompt = f"""请为"{page_element}"生成{test_goal}的A/B测试概念（流量规模：{traffic_volume}）。

请以JSON格式返回：
{{
    "page_element": "页面元素",
    "test_goal": "测试目标",
    "traffic_volume": "流量规模",
    "test_name": "测试名称",
    "hypothesis": "假设",
    "control_version": {{
        "description": "描述",
        "current_performance": "当前性能"
    }},
    "variation_versions": [
        {{
            "variation_name": "变体名称",
            "description": "描述",
            "changes_made": ["所做的更改1"],
            "expected_impact": "预期影响"
        }}
    ],
    "test_parameters": {{
        "minimum_sample_size": "最小样本量",
        "test_duration": "测试持续时间",
        "statistical_significance": "统计显著性",
        "confidence_level": "置信水平"
    }},
    "success_metrics": {{
        "primary_metric": "主要指标",
        "secondary_metrics": ["次要指标1"]
    }},
    "target_improvement": "目标改进",
    "segment_analysis": ["细分分析1"],
    "potential_interference": "潜在干扰",
    "implementation_notes": "实施说明",
    "results_interpretation_guide": "结果解释指南",
    "follow_up_tests": ["后续测试1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "page_element": page_element,
                "test_goal": test_goal,
                "traffic_volume": traffic_volume,
                **result,
            }

        except Exception as e:
            logger.error(f"生成A/B测试概念失败: {e}")
            return {
                "page_element": page_element,
                "test_goal": test_goal,
                "traffic_volume": traffic_volume,
                "test_name": "",
                "hypothesis": "",
                "control_version": {},
                "variation_versions": [],
                "test_parameters": {},
                "success_metrics": {},
                "target_improvement": "",
                "segment_analysis": [],
                "potential_interference": "",
                "implementation_notes": "",
                "results_interpretation_guide": "",
                "follow_up_tests": [],
            }


ab_test_concept_generator_service = ABTestConceptGeneratorService()