"""
Vox Video Hook Generator Service 模块

视频钩子生成服务
- 开头钩子生成
- 注意力保持
- 完播率优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class VideoHookGeneratorService:
    """
    视频钩子生成服务

    为视频生成吸引人的开头钩子
    """

    def __init__(self):
        self.llm = llm_service

    # 钩子类型
    HOOK_TYPES = [
        "question",
        "statement",
        "number",
        "场景",
        "conflict",
        "teaser",
    ]

    async def generate_hook(
        self,
        topic: str,
        duration: int = 60,
        platform: str = "tiktok",
    ) -> Dict[str, Any]:
        """
        生成视频钩子

        Args:
            topic: 主题
            duration: 时长（秒）
            platform: 平台

        Returns:
            Dict: 钩子内容
        """
        try:
            prompt = f"""请为{duration}秒的{topic}主题视频生成开头钩子。

平台：{platform}

请提供：
1. 钩子文案（3-5秒）
2. 视觉建议
3. 背景音效建议

请以JSON格式返回：
{{
    "hook_text": "钩子文案",
    "visual_suggestion": "视觉建议",
    "audio_suggestion": "音效建议",
    "duration_estimate": "预计时长"
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
                "duration": duration,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成视频钩子失败: {e}")
            return {
                "topic": topic,
                "duration": duration,
                "platform": platform,
                "hook_text": "",
                "visual_suggestion": "",
                "audio_suggestion": "",
                "duration_estimate": "",
            }

    def get_hook_types(self) -> List[str]:
        """获取钩子类型"""
        return self.HOOK_TYPES


video_hook_generator_service = VideoHookGeneratorService()