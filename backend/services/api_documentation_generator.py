"""
Vox API Documentation Generator Service 模块

API文档生成服务
- API文档
- 使用指南
- 示例代码
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class APIDocumentationGeneratorService:
    """
    API文档生成服务

    生成API文档内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_api_doc(
        self,
        api_name: str,
        endpoints: List[str],
    ) -> Dict[str, Any]:
        """
        生成API文档

        Args:
            api_name: API名称
            endpoints: 端点列表

        Returns:
            Dict: API文档内容
        """
        try:
            prompt = f"""请为"{api_name}"生成API文档。

端点：{', '.join(endpoints)}

请以JSON格式返回：
{{
    "overview": "API概述",
    "authentication": "认证方式",
    "endpoints": [
        {{
            "method": "GET",
            "path": "/endpoint",
            "description": "描述",
            "parameters": ["参数1"],
            "response_example": "响应示例"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "api_name": api_name,
                "endpoints": endpoints,
                **result,
            }

        except Exception as e:
            logger.error(f"生成API文档失败: {e}")
            return {
                "api_name": api_name,
                "endpoints": endpoints,
                "overview": "",
                "authentication": "",
                "endpoints": [],
            }


api_documentation_generator_service = APIDocumentationGeneratorService()