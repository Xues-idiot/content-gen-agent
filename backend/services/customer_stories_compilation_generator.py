"""
Vox Customer Stories Compilation Generator Service 模块

客户故事汇编生成服务
- 故事收集
- 案例亮点
- 展示优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerStoriesCompilationGeneratorService:
    """
    客户故事汇编生成服务

    生成客户故事汇编内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_stories_compilation(
        self,
        product_service: str,
        num_stories: int = 10,
        industry_focus: str = "general",
    ) -> Dict[str, Any]:
        """
        生成客户故事汇编

        Args:
            product_service: 产品/服务
            num_stories: 故事数量
            industry_focus: 行业聚焦

        Returns:
            Dict: 客户故事汇编
        """
        try:
            prompt = f"""请为"{product_service}"生成{num_stories}个客户故事汇编（行业聚焦：{industry_focus}）。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "num_stories": {num_stories},
    "industry_focus": "行业聚焦",
    "compilation_title": "汇编标题",
    "overview": "概述",
    "stories": [
        {{
            "story_title": "故事标题",
            "customer_name": "客户名称",
            "industry": "行业",
            "company_size": "公司规模",
            "challenge_brief": "挑战简报",
            "solution_applied": "应用的解决方案",
            "results_achieved": "取得的成果",
            "metrics": ["指标1"],
            "quote": "引言",
            "author_name": "作者姓名",
            "author_title": "作者职位"
        }}
    ],
    "themes_patterns": ["主题/模式1"],
    "aggregate_metrics": ["汇总指标1"],
    "industry_breakdown": ["行业细分1"],
    "key_takeaways": ["关键收获1"],
    "cta_section": "CTA部分",
    "full_stories_link": "完整故事链接"
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
                "num_stories": num_stories,
                "industry_focus": industry_focus,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户故事汇编失败: {e}")
            return {
                "product_service": product_service,
                "num_stories": num_stories,
                "industry_focus": industry_focus,
                "compilation_title": "",
                "overview": "",
                "stories": [],
                "themes_patterns": [],
                "aggregate_metrics": [],
                "industry_breakdown": [],
                "key_takeaways": [],
                "cta_section": "",
                "full_stories_link": "",
            }


customer_stories_compilation_generator_service = CustomerStoriesCompilationGeneratorService()