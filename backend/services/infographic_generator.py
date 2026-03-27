"""
Vox Infographic Text Generator Service 模块

信息图文字生成服务
- 数据可视化文案
- 图表说明
- 信息图脚本
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InfographicTextGeneratorService:
    """
    信息图文字生成服务

    生成信息图所需的文字内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_infographic_content(
        self,
        topic: str,
        data_points: List[str],
    ) -> Dict[str, Any]:
        """
        生成信息图内容

        Args:
            topic: 主题
            data_points: 数据点

        Returns:
            Dict: 信息图内容
        """
        try:
            prompt = f"""请为"{topic}"信息图生成文字内容。

数据点：{', '.join(data_points)}

请以JSON格式返回：
{{
    "title": "信息图标题",
    "sections": [
        {{
            "heading": "小标题",
            "body_text": "正文",
            "stat": "数据"
        }}
    ],
    "conclusion": "结论"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "topic": topic,
                "data_points": data_points,
                **result,
            }

        except Exception as e:
            logger.error(f"生成信息图内容失败: {e}")
            return {
                "topic": topic,
                "data_points": data_points,
                "title": "",
                "sections": [],
                "conclusion": "",
            }


infographic_text_generator_service = InfographicTextGeneratorService()