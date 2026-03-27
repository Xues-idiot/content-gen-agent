"""
Vox Podcast Script Generator Service 模块

播客脚本生成服务
- 节目大纲
- 对话脚本
- 节目笔记
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PodcastScriptGeneratorService:
    """
    播客脚本生成服务

    生成播客脚本内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_podcast_script(
        self,
        episode_title: str,
        episode_number: int,
        show_theme: str,
        duration_minutes: int = 30,
    ) -> Dict[str, Any]:
        """
        生成播客脚本

        Args:
            episode_title: 剧集标题
            episode_number: 剧集编号
            show_theme: 节目主题
            duration_minutes: 时长（分钟）

        Returns:
            Dict: 播客脚本
        """
        try:
            prompt = f"""请为"{episode_title}"（第{episode_number}集，主题：{show_theme}）生成{duration_minutes}分钟的播客脚本。

请以JSON格式返回：
{{
    "episode_title": "剧集标题",
    "episode_number": 剧集编号,
    "show_theme": "节目主题",
    "duration_minutes": {duration_minutes},
    "episode_description": "剧集描述",
    "target_listener": "目标听众",
    "intro": {{
        "hook": "开场钩子",
        "welcome_message": "欢迎信息",
        "host_introduction": "主持人介绍",
        "episode_preview": "剧集预览",
        "sponsor_message": "赞助商信息"
    }},
    "segments": [
        {{
            "segment_number": 1,
            "segment_title": "环节标题",
            "type": "类型",
            "start_time": "开始时间",
            "duration_minutes": 分钟数,
            "content": "内容",
            "key_points": ["关键点1"],
            "guest_info": "嘉宾信息",
            "sound_effects": ["音效1"],
            "music_cues": ["音乐提示1"]
        }}
    ],
    "outro": {{
        "summary": "总结",
        "call_to_action": "行动号召",
        "social_media_prompts": ["社交媒体提示1"],
        "next_episode_preview": "下集预览",
        "credits": " credits"
    }},
    "show_notes": {{
        "episode_summary": "剧集摘要",
        "timestamps": [
            {{
                "time": "时间戳",
                "topic": "主题"
            }}
        ],
        "guest_bios": ["嘉宾简介1"],
        "resources_mentioned": ["提到的资源1"],
        "links": ["链接1"]
    }},
    "transcription_ready": true
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "episode_title": episode_title,
                "episode_number": episode_number,
                "show_theme": show_theme,
                "duration_minutes": duration_minutes,
                **result,
            }

        except Exception as e:
            logger.error(f"生成播客脚本失败: {e}")
            return {
                "episode_title": episode_title,
                "episode_number": episode_number,
                "show_theme": show_theme,
                "duration_minutes": duration_minutes,
                "episode_description": "",
                "target_listener": "",
                "intro": {},
                "segments": [],
                "outro": {},
                "show_notes": {},
                "transcription_ready": False,
            }


podcast_script_generator_service = PodcastScriptGeneratorService()