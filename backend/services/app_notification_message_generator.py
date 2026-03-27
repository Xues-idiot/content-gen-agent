"""
Vox App Notification Message Generator Service 模块

应用通知消息生成服务
- 推送通知
- 应用内消息
- 提醒文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AppNotificationMessageGeneratorService:
    """
    应用通知消息生成服务

    生成应用通知消息内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_app_notification_message(
        self,
        notification_type: str,
        user_action: str,
        app_name: str,
    ) -> Dict[str, Any]:
        """
        生成应用通知消息

        Args:
            notification_type: 通知类型
            user_action: 用户操作
            app_name: 应用名称

        Returns:
            Dict: 应用通知消息
        """
        try:
            prompt = f"""请为"{app_name}"生成{notification_type}类型的{user_action}通知消息。

请以JSON格式返回：
{{
    "notification_type": "通知类型",
    "user_action": "用户操作",
    "app_name": "应用名称",
    "push_notification": {{
        "title": "标题",
        "body": "正文",
        "action_button": "操作按钮",
        "deep_link": "深度链接"
    }},
    "in_app_message": {{
        "headline": "标题",
        "message": "消息",
        "dismiss_text": "关闭文本",
        "cta_text": "CTA文本"
    }},
    "email_notification": {{
        "subject": "主题",
        "preview_text": "预览文本",
        "body": "正文"
    }},
    "sms_alternative": "SMS替代",
    "timing_recommendations": "时间建议",
    "personalization_tokens": ["个性化令牌1"],
    "frequency_guidelines": "频率指南",
    "unsubscribe_option": "取消订阅选项"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "notification_type": notification_type,
                "user_action": user_action,
                "app_name": app_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成应用通知消息失败: {e}")
            return {
                "notification_type": notification_type,
                "user_action": user_action,
                "app_name": app_name,
                "push_notification": {},
                "in_app_message": {},
                "email_notification": {},
                "sms_alternative": "",
                "timing_recommendations": "",
                "personalization_tokens": [],
                "frequency_guidelines": "",
                "unsubscribe_option": "",
            }


app_notification_message_generator_service = AppNotificationMessageGeneratorService()