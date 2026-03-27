"""
Vox UX Flow Generator Service 模块

用户体验流程生成服务
- 用户旅程
- 流程设计
- 交互路径
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class UXFlowGeneratorService:
    """
    用户体验流程生成服务

    生成用户体验流程内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_ux_flow(
        self,
        product_name: str,
        flow_type: str = "onboarding",
        num_steps: int = 7,
    ) -> Dict[str, Any]:
        """
        生成UX流程

        Args:
            product_name: 产品名称
            flow_type: 流程类型
            num_steps: 步骤数量

        Returns:
            Dict: UX流程
        """
        try:
            prompt = f"""请为"{product_name}"生成{flow_type}用户体验流程（共{num_steps}步）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "flow_type": "流程类型",
    "num_steps": 步骤数,
    "flow_title": "流程标题",
    "overview": "概述",
    "user_persona": "用户画像",
    "steps": [
        {{
            "step_number": 1,
            "step_name": "步骤名称",
            "description": "描述",
            "user_action": "用户动作",
            "system_response": "系统响应",
            "emotion": "用户情绪",
            "pain_points": ["痛点1"],
            "opportunities": ["机会1"]
        }}
    ],
    "key_metrics": ["关键指标1"],
    "optimization_suggestions": ["优化建议1"],
    "friction_points": ["摩擦点1"]
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
                "flow_type": flow_type,
                "num_steps": num_steps,
                **result,
            }

        except Exception as e:
            logger.error(f"生成UX流程失败: {e}")
            return {
                "product_name": product_name,
                "flow_type": flow_type,
                "num_steps": num_steps,
                "flow_title": "",
                "overview": "",
                "user_persona": "",
                "steps": [],
                "key_metrics": [],
                "optimization_suggestions": [],
                "friction_points": [],
            }


ux_flow_generator_service = UXFlowGeneratorService()