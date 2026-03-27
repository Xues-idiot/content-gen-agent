"""
Vox QR Code Generator Service 模块

二维码文案生成服务
- 二维码说明
- 扫码引导
- 场景文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class QRCodeCopyGeneratorService:
    """
    二维码文案生成服务

    生成二维码扫描后的落地页内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_qr_landing(
        self,
        campaign_name: str,
        destination: str,
    ) -> Dict[str, Any]:
        """
        生成二维码落地页文案

        Args:
            campaign_name: 活动名称
            destination: 目的地

        Returns:
            Dict: 落地页文案
        """
        try:
            prompt = f"""请为"{campaign_name}"生成二维码扫描后的落地页文案。

目标页面：{destination}

请以JSON格式返回：
{{
    "headline": "页面标题",
    "subheadline": "副标题",
    "value_proposition": "价值主张",
    "cta_text": "按钮文案",
    "social_proof": "社会证明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "campaign_name": campaign_name,
                "destination": destination,
                **result,
            }

        except Exception as e:
            logger.error(f"生成二维码落地页失败: {e}")
            return {
                "campaign_name": campaign_name,
                "destination": destination,
                "headline": "",
                "subheadline": "",
                "value_proposition": "",
                "cta_text": "",
                "social_proof": "",
            }


qr_code_copy_generator_service = QRCodeCopyGeneratorService()