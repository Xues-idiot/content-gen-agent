"""
Vox Testimony Compilation Generator Service 模块

证言汇编生成服务
- 客户推荐
- 用户评价
- 案例引用
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TestimonyCompilationGeneratorService:
    """
    证言汇编生成服务

    生成证言汇编内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_testimony_compilation(
        self,
        product_service: str,
        num_testimonies: int = 10,
        source_type: str = "customer",
    ) -> Dict[str, Any]:
        """
        生成证言汇编

        Args:
            product_service: 产品/服务
            num_testimonies: 证言数量
            source_type: 来源类型

        Returns:
            Dict: 证言汇编
        """
        try:
            prompt = f"""请为"{product_service}"生成{num_testimonies}条来自{source_type}类型的证言汇编。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "num_testimonies": {num_testimonies},
    "source_type": "来源类型",
    "testimonies": [
        {{
            "quote": "引言",
            "author": "作者",
            "title": "职位",
            "company": "公司",
            "relationship": "关系",
            "date": "日期",
            "rating": "评分",
            "use_case": "用例",
            "tags": ["标签1"]
        }}
    ],
    "category_groupings": [
        {{
            "category": "类别",
            "testimony_indices": [1, 2, 3]
        }}
    ],
    "summary_themes": ["总结主题1"],
    "permission_status": "许可状态",
    "attribution_requirements": "署名要求",
    "display_formats": ["展示格式1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_service": product_service,
                "num_testimonies": num_testimonies,
                "source_type": source_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成证言汇编失败: {e}")
            return {
                "product_service": product_service,
                "num_testimonies": num_testimonies,
                "source_type": source_type,
                "testimonies": [],
                "category_groupings": [],
                "summary_themes": [],
                "permission_status": "",
                "attribution_requirements": "",
                "display_formats": [],
            }


testimony_compilation_generator_service = TestimonyCompilationGeneratorService()