"""
Vox Product Update Generator Service 模块

产品更新日志生成服务
- 更新说明
- 版本发布
- 新功能介绍
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductUpdateGeneratorService:
    """
    产品更新日志生成服务

    生成产品更新说明
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_update_changelog(
        self,
        product_name: str,
        version: str,
        updates: List[str],
    ) -> Dict[str, Any]:
        """
        生成更新日志

        Args:
            product_name: 产品名称
            version: 版本号
            updates: 更新内容

        Returns:
            Dict: 更新日志
        """
        try:
            prompt = f"""请为"{product_name}"{version}版本生成更新日志。

更新内容：{', '.join(updates)}

请以JSON格式返回：
{{
    "title": "更新标题",
    "highlights": ["亮点1", "亮点2"],
    "detailed_changes": ["详细变更1"],
    "bug_fixes": ["修复1"],
    "known_issues": ["已知问题1"],
    "next_preview": "下版本预告"
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
                "version": version,
                "updates": updates,
                **result,
            }

        except Exception as e:
            logger.error(f"生成更新日志失败: {e}")
            return {
                "product_name": product_name,
                "version": version,
                "updates": updates,
                "title": "",
                "highlights": [],
                "detailed_changes": [],
                "bug_fixes": [],
                "known_issues": [],
                "next_preview": "",
            }


product_update_generator_service = ProductUpdateGeneratorService()