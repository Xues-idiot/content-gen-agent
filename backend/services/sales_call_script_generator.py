"""
Vox Sales Call Script Generator Service 模块

销售电话脚本生成服务
- 开场白
- 问题设计
- 关单话术
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesCallScriptGeneratorService:
    """
    销售电话脚本生成服务

    生成销售电话脚本内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_call_script(
        self,
        product_service: str,
        call_type: str = "discovery",
        call_duration: str = "30 min",
    ) -> Dict[str, Any]:
        """
        生成销售电话脚本

        Args:
            product_service: 产品/服务
            call_type: 电话类型
            call_duration: 电话时长

        Returns:
            Dict: 销售电话脚本
        """
        try:
            prompt = f"""请为"{product_service}"生成{call_type}类型的{call_duration}销售电话脚本。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "call_type": "电话类型",
    "call_duration": "电话时长",
    "script_sections": [
        {{
            "section": "章节",
            "duration": "时长",
            "script": "脚本",
            "objectives": ["目标1"]
        }}
    ],
    "opening_lines": ["开场白1"],
    "qualifying_questions": ["资格问题1"],
    "discovery_questions": ["发现性问题1"],
    "handling_objections": ["处理异议1"],
    "closing_lines": ["结束语1"],
    "call_flow_options": ["电话流程选项1"],
    "note_taking_template": "记笔记模板",
    "post_call_actions": ["挂电话后行动1"]
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
                "call_type": call_type,
                "call_duration": call_duration,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售电话脚本失败: {e}")
            return {
                "product_service": product_service,
                "call_type": call_type,
                "call_duration": call_duration,
                "script_sections": [],
                "opening_lines": [],
                "qualifying_questions": [],
                "discovery_questions": [],
                "handling_objections": [],
                "closing_lines": [],
                "call_flow_options": [],
                "note_taking_template": "",
                "post_call_actions": [],
            }


sales_call_script_generator_service = SalesCallScriptGeneratorService()