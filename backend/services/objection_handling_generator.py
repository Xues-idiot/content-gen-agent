"""
Vox Objection Handling Generator Service 模块

异议处理生成服务
- 常见异议
- 回应话术
- 转化策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ObjectionHandlingGeneratorService:
    """
    异议处理生成服务

    生成异议处理内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_objection_handling(
        self,
        product_service: str,
        sales_stage: str,
        num_objections: int = 10,
    ) -> Dict[str, Any]:
        """
        生成异议处理

        Args:
            product_service: 产品/服务
            sales_stage: 销售阶段
            num_objections: 异议数量

        Returns:
            Dict: 异议处理
        """
        try:
            prompt = f"""请为"{product_service}"在{sales_stage}销售阶段生成{num_objections}个异议处理内容。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "sales_stage": "销售阶段",
    "num_objections": {num_objections},
    "objections": [
        {{
            "objection": "异议",
            "category": "类别",
            "severity": "严重程度",
            "response": "回应",
            "evidence_proof": "证据/证明",
            "reframe_technique": "重构技巧"
        }}
    ],
    "empathy_statements": ["共情陈述1"],
    "bridge_statements": ["过渡陈述1"],
    "closing_techniques": ["成交技巧1"],
    "role_play_scenarios": ["角色扮演场景1"]
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
                "sales_stage": sales_stage,
                "num_objections": num_objections,
                **result,
            }

        except Exception as e:
            logger.error(f"生成异议处理失败: {e}")
            return {
                "product_service": product_service,
                "sales_stage": sales_stage,
                "num_objections": num_objections,
                "objections": [],
                "empathy_statements": [],
                "bridge_statements": [],
                "closing_techniques": [],
                "role_play_scenarios": [],
            }


objection_handling_generator_service = ObjectionHandlingGeneratorService()