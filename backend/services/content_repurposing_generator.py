"""
Vox Content Repurposing Generator Service 模块

内容再利用生成服务
- 内容改编
- 多格式转换
- 分发策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContentRepurposingGeneratorService:
    """
    内容再利用生成服务

    生成内容再利用内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_content_repurposing(
        self,
        original_content: str,
        content_type: str,
        target_formats: List[str],
    ) -> Dict[str, Any]:
        """
        生成内容再利用

        Args:
            original_content: 原始内容
            content_type: 内容类型
            target_formats: 目标格式

        Returns:
            Dict: 内容再利用
        """
        formats_str = ", ".join(target_formats)

        try:
            prompt = f"""请将"{original_content}"（{content_type}）重新用于：{formats_str}。

请以JSON格式返回：
{{
    "original_content": "原始内容",
    "content_type": "内容类型",
    "target_formats": {target_formats},
    " repurposed_content": [
        {{
            "format": "格式",
            "title": "标题",
            "content": "内容",
            "adaptation_notes": "改编说明"
        }}
    ],
    "distribution_strategy": "分发策略",
    "seo_considerations": "SEO注意事项"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "original_content": original_content,
                "content_type": content_type,
                "target_formats": target_formats,
                **result,
            }

        except Exception as e:
            logger.error(f"生成内容再利用失败: {e}")
            return {
                "original_content": original_content,
                "content_type": content_type,
                "target_formats": target_formats,
                "repurposed_content": [],
                "distribution_strategy": "",
                "seo_considerations": "",
            }


content_repurposing_generator_service = ContentRepurposingGeneratorService()