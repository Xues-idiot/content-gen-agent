"""
Vox Feature Specification Generator Service 模块

功能规格说明书生成服务
- 功能描述
- 技术要求
- 验收标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class FeatureSpecificationGeneratorService:
    """
    功能规格说明书生成服务

    生成功能规格说明书内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_feature_spec(
        self,
        feature_name: str,
        product_name: str,
        feature_type: str = "new feature",
    ) -> Dict[str, Any]:
        """
        生成功能规格说明书

        Args:
            feature_name: 功能名称
            product_name: 产品名称
            feature_type: 功能类型

        Returns:
            Dict: 功能规格说明书
        """
        try:
            prompt = f"""请为"{product_name}"的"{feature_name}"（类型：{feature_type}）生成功能规格说明书。

请以JSON格式返回：
{{
    "feature_name": "功能名称",
    "product_name": "产品名称",
    "feature_type": "功能类型",
    "overview": "概述",
    "user_story": "用户故事",
    "functional_requirements": [
        {{
            "req_id": "需求ID",
            "description": "描述",
            "priority": "优先级",
            "acceptance_criteria": "验收标准"
        }}
    ],
    "non_functional_requirements": ["非功能需求1"],
    "user_interface": {{
        "description": "界面描述",
        "screens": ["界面1"],
        "interactions": ["交互1"]
    }},
    "data_requirements": ["数据需求1"],
    "technical_specifications": ["技术规格1"],
    "dependencies": ["依赖项1"],
    "constraints": ["约束条件1"],
    "edge_cases": ["边界情况1"],
    "error_handling": "错误处理",
    "testing_requirements": ["测试需求1"],
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
                "feature_name": feature_name,
                "product_name": product_name,
                "feature_type": feature_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成功能规格说明书失败: {e}")
            return {
                "feature_name": feature_name,
                "product_name": product_name,
                "feature_type": feature_type,
                "overview": "",
                "user_story": "",
                "functional_requirements": [],
                "non_functional_requirements": [],
                "user_interface": {},
                "data_requirements": [],
                "technical_specifications": [],
                "dependencies": [],
                "constraints": [],
                "edge_cases": [],
                "error_handling": "",
                "testing_requirements": [],
                "success_metrics": "",
            }


feature_specification_generator_service = FeatureSpecificationGeneratorService()