"""
Vox Meeting Conflict Generator Service 模块

会议冲突解决生成服务
- 冲突诊断
- 沟通策略
- 和解方案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MeetingConflictGeneratorService:
    """
    会议冲突解决生成服务

    生成会议冲突解决内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_meeting_conflict(
        self,
        conflict_type: str,
        num_parties: int = 2,
        meeting_context: str = "internal",
    ) -> Dict[str, Any]:
        """
        生成会议冲突解决

        Args:
            conflict_type: 冲突类型
            num_parties: 参与方数量
            meeting_context: 会议背景

        Returns:
            Dict: 会议冲突解决
        """
        try:
            prompt = f"""请为{num_parties}方参与的{meeting_context}会议生成{conflict_type}类型的冲突解决内容。

请以JSON格式返回：
{{
    "conflict_type": "冲突类型",
    "num_parties": {num_parties},
    "meeting_context": "会议背景",
    "conflict_assessment": {{
        "root_cause": "根本原因",
        "stakeholder_positions": ["利益相关方立场1"],
        "shared_interests": ["共同利益1"]
    }},
    "facilitation_script": "促进脚本",
    "ground_rules": ["基本规则1"],
    "discussion_questions": ["讨论问题1"],
    "resolution_options": [
        {{
            "option": "选项",
            "pros": "优点",
            "cons": "缺点"
        }}
    ],
    "compromise_proposals": ["妥协提案1"],
    "next_steps": ["下一步1"],
    "follow_up_actions": ["跟进行动1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "conflict_type": conflict_type,
                "num_parties": num_parties,
                "meeting_context": meeting_context,
                **result,
            }

        except Exception as e:
            logger.error(f"生成会议冲突解决失败: {e}")
            return {
                "conflict_type": conflict_type,
                "num_parties": num_parties,
                "meeting_context": meeting_context,
                "conflict_assessment": {},
                "facilitation_script": "",
                "ground_rules": [],
                "discussion_questions": [],
                "resolution_options": [],
                "compromise_proposals": [],
                "next_steps": [],
                "follow_up_actions": [],
            }


meeting_conflict_generator_service = MeetingConflictGeneratorService()