"""
Vox Objection Handling Guide Generator Service 模块

异议处理指南生成服务
- 常见异议
- 响应策略
- 话术示例
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ObjectionHandlingGuideGeneratorService:
    """
    异议处理指南生成服务

    生成异议处理指南内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_objection_handling_guide(
        self,
        product_category: str,
        num_objections: int = 10,
    ) -> Dict[str, Any]:
        """
        生成异议处理指南

        Args:
            product_category: 产品类别
            num_objections: 异议数量

        Returns:
            Dict: 异议处理指南
        """
        try:
            prompt = f"""请为{product_category}产品类别生成{num_objections}个常见异议的处理指南。

请以JSON格式返回：
{{
    "product_category": "产品类别",
    "num_objections": {num_objections},
    "guide_title": "指南标题",
    "objections": [
        {{
            "objection_category": "异议类别",
            "objection_text": "异议文本",
            "root_cause": "根本原因",
            "response_strategy": "响应策略",
            "sample_responses": ["示例响应1"],
            "compelling_evidence": ["有说服力的证据1"]
        }}
    ],
    "general_principles": ["一般原则1"],
    "tone_guidance": "语气指导",
    "closing_techniques": ["成交技巧1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_category": product_category,
                "num_objections": num_objections,
                **result,
            }

        except Exception as e:
            logger.error(f"生成异议处理指南失败: {e}")
            return {
                "product_category": product_category,
                "num_objections": num_objections,
                "guide_title": "",
                "objections": [],
                "general_principles": [],
                "tone_guidance": "",
                "closing_techniques": [],
            }


objection_handling_guide_generator_service = ObjectionHandlingGuideGeneratorService()
