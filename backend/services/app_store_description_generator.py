"""
Vox App Store Description Generator Service 模块

应用商店描述生成服务
- 应用描述
- 关键词优化
- 截图文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AppStoreDescriptionGeneratorService:
    """
    应用商店描述生成服务

    生成应用商店描述内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_app_store_description(
        self,
        app_name: str,
        app_category: str,
        key_features: List[str],
    ) -> Dict[str, Any]:
        """
        生成应用商店描述

        Args:
            app_name: 应用名称
            app_category: 应用类别
            key_features: 关键功能

        Returns:
            Dict: 应用商店描述
        """
        features_str = ", ".join(key_features[:5])

        try:
            prompt = f"""请为"{app_name}"（{app_category}）生成应用商店描述（关键功能：{features_str}）。

请以JSON格式返回：
{{
    "app_name": "应用名称",
    "app_category": "应用类别",
    "key_features": {key_features},
    "app_title": "应用标题",
    "short_description": "短描述",
    "full_description": "完整描述",
    "keywords": ["关键词1"],
    "whats_new": "新增内容",
    "screenshot_captions": ["截图标题1"],
    "preview_video_notes": "预览视频说明",
    "localization_notes": "本地化说明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "app_name": app_name,
                "app_category": app_category,
                "key_features": key_features,
                **result,
            }

        except Exception as e:
            logger.error(f"生成应用商店描述失败: {e}")
            return {
                "app_name": app_name,
                "app_category": app_category,
                "key_features": key_features,
                "app_title": "",
                "short_description": "",
                "full_description": "",
                "keywords": [],
                "whats_new": "",
                "screenshot_captions": [],
                "preview_video_notes": "",
                "localization_notes": "",
            }


app_store_description_generator_service = AppStoreDescriptionGeneratorService()