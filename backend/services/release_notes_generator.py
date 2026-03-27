"""
Vox Release Notes Generator Service 模块

发布说明生成服务
- 版本更新
- 变更日志
- 迁移指南
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ReleaseNotesGeneratorService:
    """
    发布说明生成服务

    生成发布说明内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_release_notes(
        self,
        product_name: str,
        version: str,
        release_date: str,
    ) -> Dict[str, Any]:
        """
        生成发布说明

        Args:
            product_name: 产品名称
            version: 版本号
            release_date: 发布日期

        Returns:
            Dict: 发布说明
        """
        try:
            prompt = f"""请为"{product_name}"版本{version}（发布日期：{release_date}）生成发布说明。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "version": "版本号",
    "release_date": "发布日期",
    "release_type": "发布类型",
    "overview": "概述",
    "new_features": [
        {{
            "feature": "功能名称",
            "description": "描述",
            "category": "类别"
        }}
    ],
    "improvements": [
        {{
            "improvement": "改进名称",
            "description": "描述",
            "impact": "影响"
        }}
    ],
    "bug_fixes": ["修复1"],
    "known_issues": ["已知问题1"],
    "deprecations": ["废弃1"],
    "breaking_changes": ["破坏性变更1"],
    "migration_guide": "迁移指南",
    "upgrade_notice": "升级通知",
    "download_links": ["下载链接1"],
    "support_information": "支持信息"
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
                "release_date": release_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成发布说明失败: {e}")
            return {
                "product_name": product_name,
                "version": version,
                "release_date": release_date,
                "release_type": "",
                "overview": "",
                "new_features": [],
                "improvements": [],
                "bug_fixes": [],
                "known_issues": [],
                "deprecations": [],
                "breaking_changes": [],
                "migration_guide": "",
                "upgrade_notice": "",
                "download_links": [],
                "support_information": "",
            }


release_notes_generator_service = ReleaseNotesGeneratorService()