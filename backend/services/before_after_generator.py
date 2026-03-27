"""
Vox Before/After Generator Service 模块

前后对比生成服务
- 转变展示
- 效果可视化
- 故事叙述
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BeforeAfterGeneratorService:
    """
    前后对比生成服务

    生成前后对比内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_comparison(
        self,
        subject: str,
        comparison_type: str = "transformation",
    ) -> Dict[str, Any]:
        """
        生成前后对比

        Args:
            subject: 对比主题
            comparison_type: 对比类型

        Returns:
            Dict: 对比内容
        """
        try:
            prompt = f"""请为"{subject}"生成一个前后对比内容。

类型：{comparison_type}

请以JSON格式返回：
{{
    "title": "标题",
    "before_state": "使用前状态",
    "after_state": "使用后状态",
    "key_differences": ["差异1", "差异2"],
    "story_angle": "故事角度"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "subject": subject,
                "comparison_type": comparison_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成前后对比失败: {e}")
            return {
                "subject": subject,
                "comparison_type": comparison_type,
                "title": "",
                "before_state": "",
                "after_state": "",
                "key_differences": [],
                "story_angle": "",
            }


before_after_generator_service = BeforeAfterGeneratorService()