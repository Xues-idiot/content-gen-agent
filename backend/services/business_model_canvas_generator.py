"""
Vox Business Model Canvas Generator Service 模块

商业模式画布生成服务
- 价值主张
- 渠道通路
- 收入来源
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BusinessModelCanvasGeneratorService:
    """
    商业模式画布生成服务

    生成商业模式画布内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_business_model_canvas(
        self,
        business_name: str,
        industry: str,
    ) -> Dict[str, Any]:
        """
        生成商业模式画布

        Args:
            business_name: 业务名称
            industry: 行业

        Returns:
            Dict: 商业模式画布
        """
        try:
            prompt = f"""请为"{business_name}"（{industry}行业）生成商业模式画布。

请以JSON格式返回：
{{
    "business_name": "业务名称",
    "industry": "行业",
    "key_partners": ["关键合作伙伴1"],
    "key_activities": ["关键活动1"],
    "key_resources": ["关键资源1"],
    "value_propositions": ["价值主张1"],
    "customer_relationships": ["客户关系1"],
    "channels": ["渠道1"],
    "customer_segments": ["客户细分1"],
    "cost_structure": ["成本结构1"],
    "revenue_streams": ["收入来源1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "business_name": business_name,
                "industry": industry,
                **result,
            }

        except Exception as e:
            logger.error(f"生成商业模式画布失败: {e}")
            return {
                "business_name": business_name,
                "industry": industry,
                "key_partners": [],
                "key_activities": [],
                "key_resources": [],
                "value_propositions": [],
                "customer_relationships": [],
                "channels": [],
                "customer_segments": [],
                "cost_structure": [],
                "revenue_streams": [],
            }


business_model_canvas_generator_service = BusinessModelCanvasGeneratorService()
