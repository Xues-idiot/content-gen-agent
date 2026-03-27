"""
Vox Feature Highlight Generator Service 模块

功能亮点生成服务
- 核心功能
- 差异化卖点
- 使用场景
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class FeatureHighlightGeneratorService:
    """
    功能亮点生成服务

    生成产品功能亮点内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_highlights(
        self,
        product_name: str,
        features: List[str],
    ) -> List[Dict[str, Any]]:
        """
        生成功能亮点

        Args:
            product_name: 产品名称
            features: 功能列表

        Returns:
            List[Dict]: 亮点列表
        """
        try:
            prompt = f"""请为"{product_name}"的以下功能生成亮点描述：

功能：{', '.join(features)}

请以JSON格式返回：
{{
    "highlights": [
        {{
            "feature": "功能名称",
            "highlight": "亮点描述",
            "benefit": "用户收益"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return result.get("highlights", [])

        except Exception as e:
            logger.error(f"生成功能亮点失败: {e}")
            return []


feature_highlight_generator_service = FeatureHighlightGeneratorService()