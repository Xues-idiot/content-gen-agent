"""
Vox Chatbot Script Generator Service 模块

聊天机器人脚本生成服务
- 对话脚本
- 问答设计
- 情感响应
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ChatbotScriptGeneratorService:
    """
    聊天机器人脚本生成服务

    生成聊天机器人对话脚本
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_chatbot_script(
        self,
        use_case: str,
        personality: str = "friendly",
    ) -> Dict[str, Any]:
        """
        生成聊天脚本

        Args:
            use_case: 使用场景
            personality: 个性

        Returns:
            Dict: 聊天脚本
        """
        try:
            prompt = f"""请为"{use_case}"场景生成聊天机器人脚本。

个性：{personality}

请以JSON格式返回：
{{
    "greeting": "问候语",
    "conversational_flows": [
        {{
            "user_input": "用户输入",
            "bot_response": "机器人回复"
        }}
    ],
    "fallback_responses": ["默认回复1"],
    "closing": "结束语"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "use_case": use_case,
                "personality": personality,
                **result,
            }

        except Exception as e:
            logger.error(f"生成聊天脚本失败: {e}")
            return {
                "use_case": use_case,
                "personality": personality,
                "greeting": "",
                "conversational_flows": [],
                "fallback_responses": [],
                "closing": "",
            }


chatbot_script_generator_service = ChatbotScriptGeneratorService()