"""
Vox Mindmap Content Generator Service 模块

思维导图内容生成服务
- 主题展开
- 分支结构
- 内容层次
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MindmapContentGeneratorService:
    """
    思维导图内容生成服务

    生成思维导图内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_mindmap_content(
        self,
        central_topic: str,
        depth: int = 3,
        branch_count: int = 5,
    ) -> Dict[str, Any]:
        """
        生成思维导图内容

        Args:
            central_topic: 中心主题
            depth: 深度
            branch_count: 分支数量

        Returns:
            Dict: 思维导图内容
        """
        try:
            prompt = f"""请为"{central_topic}"生成思维导图内容（深度：{depth}，分支数：{branch_count}）。

请以JSON格式返回：
{{
    "central_topic": "中心主题",
    "depth": 深度,
    "branch_count": 分支数,
    "mindmap_structure": {{
        "center": "中心节点",
        "branches": [
            {{
                "branch_name": "分支名称",
                "subtopics": ["子主题1"],
                "details": ["详细内容1"]
            }}
        ]
    }},
    "key_concepts": ["关键概念1"],
    "relationships": ["关联1"],
    "visualization_tips": ["可视化建议1"],
    "color_coding_suggestions": "颜色编码建议"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "central_topic": central_topic,
                "depth": depth,
                "branch_count": branch_count,
                **result,
            }

        except Exception as e:
            logger.error(f"生成思维导图内容失败: {e}")
            return {
                "central_topic": central_topic,
                "depth": depth,
                "branch_count": branch_count,
                "mindmap_structure": {},
                "key_concepts": [],
                "relationships": [],
                "visualization_tips": [],
                "color_coding_suggestions": "",
            }


mindmap_content_generator_service = MindmapContentGeneratorService()