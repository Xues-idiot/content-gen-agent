"""
Vox Corporate Video Script Generator Service 模块

企业视频脚本生成服务
- 宣传视频
- 介绍视频
- 培训视频
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CorporateVideoScriptGeneratorService:
    """
    企业视频脚本生成服务

    生成企业视频脚本内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_corporate_video_script(
        self,
        video_title: str,
        video_type: str = "promotional",
        duration_minutes: int = 3,
    ) -> Dict[str, Any]:
        """
        生成企业视频脚本

        Args:
            video_title: 视频标题
            video_type: 视频类型
            duration_minutes: 时长

        Returns:
            Dict: 企业视频脚本
        """
        try:
            prompt = f"""请为"{video_title}"（类型：{video_type}，时长：{duration_minutes}分钟）生成视频脚本。

请以JSON格式返回：
{{
    "video_title": "视频标题",
    "video_type": "视频类型",
    "duration_minutes": 时长,
    "target_audience": "目标受众",
    "key_message": "关键信息",
    "script": [
        {{
            "scene_number": 1,
            "scene_description": "场景描述",
            "visuals": "视觉",
            "audio": "音频",
            "dialogue_narration": "对话/旁白",
            "duration_seconds": 秒数,
            "notes": "备注"
        }}
    ],
    "voiceover_script": "旁白脚本",
    "music_and_sound_effects": "音乐和音效",
    "on_screen_text": "屏幕文字",
    "call_to_action": "行动号召",
    "production_notes": "制作备注",
    "technical_requirements": "技术要求"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "video_title": video_title,
                "video_type": video_type,
                "duration_minutes": duration_minutes,
                **result,
            }

        except Exception as e:
            logger.error(f"生成企业视频脚本失败: {e}")
            return {
                "video_title": video_title,
                "video_type": video_type,
                "duration_minutes": duration_minutes,
                "target_audience": "",
                "key_message": "",
                "script": [],
                "voiceover_script": "",
                "music_and_sound_effects": "",
                "on_screen_text": "",
                "call_to_action": "",
                "production_notes": "",
                "technical_requirements": "",
            }


corporate_video_script_generator_service = CorporateVideoScriptGeneratorService()