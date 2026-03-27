"""
Vox UX Research Plan Generator Service 模块

UX研究计划生成服务
- 研究目标
- 方法论
- 参与者招募
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class UXResearchPlanGeneratorService:
    """
    UX研究计划生成服务

    生成UX研究计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_ux_research_plan(
        self,
        research_topic: str,
        target_users: str,
        num_methods: int = 4,
    ) -> Dict[str, Any]:
        """
        生成UX研究计划

        Args:
            research_topic: 研究主题
            target_users: 目标用户
            num_methods: 方法数量

        Returns:
            Dict: UX研究计划
        """
        try:
            prompt = f"""请为"{research_topic}"研究主题生成针对{target_users}的{num_methods}种方法的UX研究计划。

请以JSON格式返回：
{{
    "research_topic": "研究主题",
    "target_users": "目标用户",
    "num_methods": {num_methods},
    "executive_summary": "执行摘要",
    "research_objectives": ["研究目标1"],
    "research_methods": [
        {{
            "method_name": "方法名称",
            "description": "描述",
            "sample_size": "样本量",
            "duration": "持续时间",
            "key_questions": ["关键问题1"],
            "deliverables": ["可交付成果1"]
        }}
    ],
    "participant_recruitment": "参与者招募",
    "screening_criteria": "筛选标准",
    "discussion_guide_outline": "讨论指南大纲",
    "timeline_and_milestones": ["时间线和里程碑1"],
    "budget_estimate": "预算估计",
    "analysis_approach": "分析方法",
    "stakeholder_presentation": "利益相关者演示"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "research_topic": research_topic,
                "target_users": target_users,
                "num_methods": num_methods,
                **result,
            }

        except Exception as e:
            logger.error(f"生成UX研究计划失败: {e}")
            return {
                "research_topic": research_topic,
                "target_users": target_users,
                "num_methods": num_methods,
                "executive_summary": "",
                "research_objectives": [],
                "research_methods": [],
                "participant_recruitment": "",
                "screening_criteria": "",
                "discussion_guide_outline": "",
                "timeline_and_milestones": [],
                "budget_estimate": "",
                "analysis_approach": "",
                "stakeholder_presentation": "",
            }


ux_research_plan_generator_service = UXResearchPlanGeneratorService()
