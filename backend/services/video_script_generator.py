"""
Vox Video Script Generator Service 模块

视频脚本生成服务
- 短视频脚本
- 分镜头脚本
- 口播文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class VideoScriptGeneratorService:
    """
    视频脚本生成服务

    生成视频拍摄脚本
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_script(
        self,
        topic: str,
        duration: int = 60,
        script_type: str = "short_video",
    ) -> Dict[str, Any]:
        """
        生成视频脚本

        Args:
            topic: 主题
            duration: 时长（秒）
            script_type: 脚本类型

        Returns:
            Dict: 脚本内容
        """
        try:
            prompt = f"""请为"{topic}"生成一个{duration}秒的{script_type}视频脚本。

请以JSON格式返回：
{{
    "title": "脚本标题",
    "scenes": [
        {{
            "scene": 1,
            "duration": 5,
            "shot": "镜头描述",
            "dialogue": "台词",
            "music": "音乐建议"
        }}
    ],
    "total_duration": {duration}
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
                "script_type": script_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成视频脚本失败: {e}")
            return {
                "topic": topic,
                "duration": duration,
                "script_type": script_type,
                "title": "",
                "scenes": [],
                "total_duration": duration,
            }


video_script_generator_service = VideoScriptGeneratorService()