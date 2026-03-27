"""
Vox Brand Voice Analyzer Service 模块

品牌调性分析服务
- 品牌声音分析
- 一致性检查
- 调性优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandVoiceAnalyzerService:
    """
    品牌调性分析服务

    分析和保持品牌调性一致性
    """

    def __init__(self):
        self.llm = llm_service

    # 品牌调性类型
    VOICE_TYPES = [
        "professional",
        "friendly",
        "bold",
        "sophisticated",
        "playful",
        "inspirational",
    ]

    async def analyze_content_voice(
        self,
        content: str,
        expected_voice: str,
    ) -> Dict[str, Any]:
        """
        分析内容调性

        Args:
            content: 内容
            expected_voice: 期望的调性

        Returns:
            Dict: 分析结果
        """
        try:
            prompt = f"""请分析以下内容的品牌调性。

期望调性：{expected_voice}
内容：{content[:500]}

请以JSON格式返回：
{{
    "actual_voice": "实际调性",
    "match_score": 0-100,
    "deviations": ["偏差1"],
    "suggestions": ["建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "expected_voice": expected_voice,
                **result,
            }

        except Exception as e:
            logger.error(f"分析品牌调性失败: {e}")
            return {
                "expected_voice": expected_voice,
                "actual_voice": "",
                "match_score": 0,
                "deviations": [],
                "suggestions": [],
            }

    def get_voice_types(self) -> List[str]:
        """获取调性类型"""
        return self.VOICE_TYPES


brand_voice_analyzer_service = BrandVoiceAnalyzerService()