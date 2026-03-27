"""
Vox Data Governance Framework Generator Service 模块

数据治理框架生成服务
- 数据质量
- 隐私合规
- 治理流程
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DataGovernanceFrameworkGeneratorService:
    """
    数据治理框架生成服务

    生成数据治理框架内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_data_governance_framework(
        self,
        organization: str,
        scope: str,
        num_domains: int = 6,
    ) -> Dict[str, Any]:
        """
        生成数据治理框架

        Args:
            organization: 组织
            scope: 范围
            num_domains: 领域数量

        Returns:
            Dict: 数据治理框架
        """
        try:
            prompt = f"""请为{organization}的{scope}范围生成{num_domains}个领域的数据治理框架。

请以JSON格式返回：
{{
    "organization": "组织",
    "scope": "范围",
    "num_domains": {num_domains},
    "executive_summary": "执行摘要",
    "governance_domains": [
        {{
            "domain_name": "领域名称",
            "policies": ["政策1"],
            "standards": ["标准1"],
            "procedures": ["程序1"],
            "stakeholders": ["利益相关者1"]
        }}
    ],
    "data_quality_dimensions": ["数据质量维度1"],
    "privacy_compliance": "隐私合规",
    "data_stewardship_model": "数据管理模型",
    "technology_enablers": ["技术推动者1"],
    "implementation_priority": "实施优先级",
    "success_metrics": ["成功指标1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "organization": organization,
                "scope": scope,
                "num_domains": num_domains,
                **result,
            }

        except Exception as e:
            logger.error(f"生成数据治理框架失败: {e}")
            return {
                "organization": organization,
                "scope": scope,
                "num_domains": num_domains,
                "executive_summary": "",
                "governance_domains": [],
                "data_quality_dimensions": [],
                "privacy_compliance": "",
                "data_stewardship_model": "",
                "technology_enablers": [],
                "implementation_priority": "",
                "success_metrics": [],
            }


data_governance_framework_generator_service = DataGovernanceFrameworkGeneratorService()
