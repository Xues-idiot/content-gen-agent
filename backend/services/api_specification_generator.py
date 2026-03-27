"""
Vox API Specification Generator Service 模块

API规格生成服务
- 接口文档
- 参数说明
- 示例代码
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class APISpecificationGeneratorService:
    """
    API规格生成服务

    生成API规格内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_api_spec(
        self,
        api_name: str,
        api_version: str = "1.0",
        num_endpoints: int = 5,
    ) -> Dict[str, Any]:
        """
        生成API规格

        Args:
            api_name: API名称
            api_version: API版本
            num_endpoints: 端点数量

        Returns:
            Dict: API规格
        """
        try:
            prompt = f"""请为"{api_name}"（版本：{api_version}）生成{num_endpoints}个端点的API规格。

请以JSON格式返回：
{{
    "api_name": "API名称",
    "api_version": "API版本",
    "base_url": "基础URL",
    "overview": "概述",
    "authentication": "认证方式",
    "endpoints": [
        {{
            "method": "HTTP方法",
            "path": "路径",
            "description": "描述",
            "parameters": [
                {{
                    "name": "参数名",
                    "type": "类型",
                    "required": "是否必填",
                    "description": "描述"
                }}
            ],
            "request_body": "请求体",
            "response": "响应",
            "example_request": "请求示例",
            "example_response": "响应示例",
            "error_codes": ["错误码1"]
        }}
    ],
    "rate_limiting": "速率限制",
    "pagination": "分页",
    "webhooks": ["Webhook1"],
    "sdks": ["SDK1"],
    "changelog": "变更日志"
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
                "api_version": api_version,
                "num_endpoints": num_endpoints,
                **result,
            }

        except Exception as e:
            logger.error(f"生成API规格失败: {e}")
            return {
                "api_name": api_name,
                "api_version": api_version,
                "num_endpoints": num_endpoints,
                "base_url": "",
                "overview": "",
                "authentication": "",
                "endpoints": [],
                "rate_limiting": "",
                "pagination": "",
                "webhooks": [],
                "sdks": [],
                "changelog": "",
            }


api_specification_generator_service = APISpecificationGeneratorService()