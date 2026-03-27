"""
Vox Product Update Announcement Generator Service 模块

产品更新公告生成服务
- 更新说明
- 亮点介绍
- 迁移指南
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductUpdateAnnouncementGeneratorService:
    """
    产品更新公告生成服务

    生成产品更新公告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_update_announcement(
        self,
        product_name: str,
        version: str,
        update_type: str = "feature",
    ) -> Dict[str, Any]:
        """
        生成产品更新公告

        Args:
            product_name: 产品名称
            version: 版本
            update_type: 更新类型

        Returns:
            Dict: 产品更新公告
        """
        try:
            prompt = f"""请为"{product_name}"（v{version}）生成{update_type}类型的产品更新公告。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "version": "版本",
    "update_type": "更新类型",
    "announcement_headline": "公告标题",
    "summary": "摘要",
    "new_features": [
        {{
            "feature_name": "功能名称",
            "description": "描述",
            "how_to_access": "如何访问",
            "screenshot_needed": true
        }}
    ],
    "improvements": [
        {{
            "area": "领域",
            "before": "之前",
            "after": "之后"
        }}
    ],
    "bug_fixes": ["错误修复1"],
    "breaking_changes": ["破坏性更改1"],
    "deprecations": ["弃用1"],
    "migration_guide": "迁移指南",
    "rollback_options": "回滚选项",
    "known_issues": ["已知问题1"],
    "next_steps": ["下一步1"],
    "feedback_cta": "反馈CTA",
    "support_resources": ["支持资源1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "version": version,
                "update_type": update_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品更新公告失败: {e}")
            return {
                "product_name": product_name,
                "version": version,
                "update_type": update_type,
                "announcement_headline": "",
                "summary": "",
                "new_features": [],
                "improvements": [],
                "bug_fixes": [],
                "breaking_changes": [],
                "deprecations": [],
                "migration_guide": "",
                "rollback_options": "",
                "known_issues": [],
                "next_steps": [],
                "feedback_cta": "",
                "support_resources": [],
            }


product_update_announcement_generator_service = ProductUpdateAnnouncementGeneratorService()