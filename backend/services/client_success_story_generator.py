"""
Vox Client Success Story Generator Service 模块

客户成功故事生成服务
- 客户案例
- 成功故事
- 效果展示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ClientSuccessStoryGeneratorService:
    """
    客户成功故事生成服务

    生成客户成功故事内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_success_story(
        self,
        client_name: str,
        industry: str,
        problem_brief: str,
        solution_brief: str,
    ) -> Dict[str, Any]:
        """
        生成客户成功故事

        Args:
            client_name: 客户名称
            industry: 行业
            problem_brief: 问题简述
            solution_brief: 解决方案简述

        Returns:
            Dict: 客户成功故事
        """
        try:
            prompt = f"""请为"{client_name}"（{industry}行业）生成客户成功故事。

问题：{problem_brief}
解决方案：{solution_brief}

请以JSON格式返回：
{{
    "client_name": "客户名称",
    "industry": "行业",
    "story_title": "故事标题",
    "executive_summary": "执行摘要",
    "client_background": "客户背景",
    "challenge": "挑战",
    "solution": "解决方案",
    "implementation": "实施过程",
    "results": [
        {{
            "metric": "指标",
            "before": "之前",
            "after": "之后",
            "improvement": "提升"
        }}
    ],
    "testimonial": "客户评价",
    "lessons_learned": "经验教训",
    "about_company": "关于公司"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "client_name": client_name,
                "industry": industry,
                "problem_brief": problem_brief,
                "solution_brief": solution_brief,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户成功故事失败: {e}")
            return {
                "client_name": client_name,
                "industry": industry,
                "problem_brief": problem_brief,
                "solution_brief": solution_brief,
                "story_title": "",
                "executive_summary": "",
                "client_background": "",
                "challenge": "",
                "solution": "",
                "implementation": "",
                "results": [],
                "testimonial": "",
                "lessons_learned": "",
                "about_company": "",
            }


client_success_story_generator_service = ClientSuccessStoryGeneratorService()