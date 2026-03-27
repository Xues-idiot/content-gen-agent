"""
Vox Infographic Content Generator Service 模块

信息图内容生成服务
- 数据可视化
- 统计展示
- 流程图
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InfographicContentGeneratorService:
    """
    信息图内容生成服务

    生成信息图内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_infographic_content(
        self,
        topic: str,
        data_points: List[str],
        infographic_type: str = "statistics",
    ) -> Dict[str, Any]:
        """
        生成信息图内容

        Args:
            topic: 主题
            data_points: 数据点
            infographic_type: 信息图类型

        Returns:
            Dict: 信息图内容
        """
        try:
            data_str = ", ".join(data_points)
            prompt = f"""请为"{topic}"生成{data_points}类型的信息图内容（类型：{infographic_type}）。

请以JSON格式返回：
{{
    "title": "标题",
    "topic": "主题",
    "infographic_type": "信息图类型",
    "visual_style": "视觉风格",
    "color_scheme": "配色方案",
    "sections": [
        {{
            "section_title": "章节标题",
            "visual_type": "可视化类型",
            "content": "内容",
            "data_points": ["数据点1"]
        }}
    ],
    "statistics": [
        {{
            "stat": "统计数字",
            "label": "标签",
            "source": "来源"
        }}
    ],
    "icons_suggested": ["建议图标1"],
    "charts_recommended": ["推荐图表1"],
    "layout_structure": "布局结构",
    "text_content": {{
        "headline": "标题",
        "subheadline": "副标题",
        "body_text": "正文",
        "captions": [" caption1"]
    }},
    "sources_and_citations": ["来源和引用1"],
    "design_notes": "设计说明",
    "accessibility_considerations": "无障碍考虑"
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
                "infographic_type": infographic_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成信息图内容失败: {e}")
            return {
                "topic": topic,
                "data_points": data_points,
                "infographic_type": infographic_type,
                "title": "",
                "visual_style": "",
                "color_scheme": "",
                "sections": [],
                "statistics": [],
                "icons_suggested": [],
                "charts_recommended": [],
                "layout_structure": "",
                "text_content": {},
                "sources_and_citations": [],
                "design_notes": "",
                "accessibility_considerations": "",
            }


infographic_content_generator_service = InfographicContentGeneratorService()