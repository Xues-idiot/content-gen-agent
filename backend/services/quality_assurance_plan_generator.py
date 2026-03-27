"""
Vox Quality Assurance Plan Generator Service 模块

质量保证计划生成服务
- 测试策略
- 测试用例
- 质量标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class QualityAssurancePlanGeneratorService:
    """
    质量保证计划生成服务

    生成质量保证计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_quality_assurance_plan(
        self,
        project_name: str,
        testing_scope: str,
        num_test_cases: int = 10,
    ) -> Dict[str, Any]:
        """
        生成质量保证计划

        Args:
            project_name: 项目名称
            testing_scope: 测试范围
            num_test_cases: 测试用例数量

        Returns:
            Dict: 质量保证计划
        """
        try:
            prompt = f"""请为"{project_name}"（测试范围：{testing_scope}）生成{num_test_cases}个测试用例的质量保证计划。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "testing_scope": "测试范围",
    "num_test_cases": {num_test_cases},
    "executive_summary": "执行摘要",
    "testing_strategy": "测试策略",
    "test_types": ["测试类型1"],
    "test_cases": [
        {{
            "test_case_id": "测试用例ID",
            "test_case_name": "测试用例名称",
            "test_objective": "测试目标",
            "preconditions": "前置条件",
            "test_steps": ["测试步骤1"],
            "expected_results": "预期结果",
            "priority": "优先级"
        }}
    ],
    "quality_metrics": ["质量指标1"],
    "defect_tracking": "缺陷跟踪",
    "test_environment": "测试环境",
    "test_schedule": "测试计划",
    "risks_and_mitigation": ["风险和缓解1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_name": project_name,
                "testing_scope": testing_scope,
                "num_test_cases": num_test_cases,
                **result,
            }

        except Exception as e:
            logger.error(f"生成质量保证计划失败: {e}")
            return {
                "project_name": project_name,
                "testing_scope": testing_scope,
                "num_test_cases": num_test_cases,
                "executive_summary": "",
                "testing_strategy": "",
                "test_types": [],
                "test_cases": [],
                "quality_metrics": [],
                "defect_tracking": "",
                "test_environment": "",
                "test_schedule": "",
                "risks_and_mitigation": [],
            }


quality_assurance_plan_generator_service = QualityAssurancePlanGeneratorService()
