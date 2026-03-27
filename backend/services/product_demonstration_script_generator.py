"""
Vox Product Demonstration Script Generator Service 模块

产品演示脚本生成服务
- 演示流程
- 功能展示
- 异议处理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductDemonstrationScriptGeneratorService:
    """
    产品演示脚本生成服务

    生成产品演示脚本内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_demonstration_script(
        self,
        product_name: str,
        demo_length: str,
        audience_type: str,
    ) -> Dict[str, Any]:
        """
        生成产品演示脚本

        Args:
            product_name: 产品名称
            demo_length: 演示长度
            audience_type: 受众类型

        Returns:
            Dict: 产品演示脚本
        """
        try:
            prompt = f"""请为"{product_name}"生成{audience_type}受众的{demo_length}产品演示脚本。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "demo_length": "演示长度",
    "audience_type": "受众类型",
    "script_sections": [
        {{
            "section": "章节",
            "duration": "时长",
            "script": "脚本",
            "key_points": ["关键点1"]
        }}
    ],
    "feature_demos": [
        {{
            "feature": "功能",
            "demo_steps": ["演示步骤1"],
            "benefits_to_emphasize": ["要强调的好处1"]
        }}
    ],
    "objection_handling": ["异议处理1"],
    "live_drill_down": ["实时深入1"],
    "success_story_integration": "成功案例整合",
    "qa_preparation": "问答准备",
    "closing_approach": "结束方式"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "demo_length": demo_length,
                "audience_type": audience_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品演示脚本失败: {e}")
            return {
                "product_name": product_name,
                "demo_length": demo_length,
                "audience_type": audience_type,
                "script_sections": [],
                "feature_demos": [],
                "objection_handling": [],
                "live_drill_down": [],
                "success_story_integration": "",
                "qa_preparation": "",
                "closing_approach": "",
            }


product_demonstration_script_generator_service = ProductDemonstrationScriptGeneratorService()