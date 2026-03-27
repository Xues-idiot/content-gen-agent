"""
Vox Customer Feedback Request Generator Service 模块

客户反馈请求生成服务
- 反馈邀请
- 调查链接
- 激励措施
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerFeedbackRequestGeneratorService:
    """
    客户反馈请求生成服务

    生成客户反馈请求内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_feedback_request(
        self,
        context: str,
        feedback_type: str,
        num_channels: int = 3,
    ) -> Dict[str, Any]:
        """
        生成客户反馈请求

        Args:
            context: 背景
            feedback_type: 反馈类型
            num_channels: 渠道数量

        Returns:
            Dict: 客户反馈请求
        """
        try:
            prompt = f"""请为"{context}"生成{num_channels}个渠道的{feedback_type}类型客户反馈请求。

请以JSON格式返回：
{{
    "context": "背景",
    "feedback_type": "反馈类型",
    "num_channels": {num_channels},
    "request_templates": [
        {{
            "channel": "渠道",
            "subject": "主题",
            "body": "正文",
            "incentive_offered": "提供的激励"
        }}
    ],
    "survey_questions": ["调查问题1"],
    "timing_recommendations": "时机建议",
    "follow_up_strategy": "跟进策略"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "context": context,
                "feedback_type": feedback_type,
                "num_channels": num_channels,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户反馈请求失败: {e}")
            return {
                "context": context,
                "feedback_type": feedback_type,
                "num_channels": num_channels,
                "request_templates": [],
                "survey_questions": [],
                "timing_recommendations": "",
                "follow_up_strategy": "",
            }


customer_feedback_request_generator_service = CustomerFeedbackRequestGeneratorService()