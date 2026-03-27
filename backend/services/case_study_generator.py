"""
Vox Case Study Generator Service 模块

案例研究生成服务
- 客户案例
- 成功故事
- 效果展示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CaseStudyGeneratorService:
    """
    案例研究生成服务

    生成客户案例研究内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_case_study(
        self,
        client_name: str,
        industry: str,
        challenge: str,
    ) -> Dict[str, Any]:
        """
        生成案例研究

        Args:
            client_name: 客户名称
            industry: 行业
            challenge: 挑战

        Returns:
            Dict: 案例研究内容
        """
        try:
            prompt = f"""请为"{client_name}"生成一个案例研究。

行业：{industry}
挑战：{challenge}

请以JSON格式返回：
{{
    "title": "案例标题",
    "client": "客户名称",
    "challenge": "挑战描述",
    "solution": "解决方案",
    "results": ["结果1", "结果2"],
    "testimonial": "客户评价"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "client_name": client_name,
                "industry": industry,
                "challenge": challenge,
                **result,
            }

        except Exception as e:
            logger.error(f"生成案例研究失败: {e}")
            return {
                "client_name": client_name,
                "industry": industry,
                "challenge": challenge,
                "title": "",
                "client": "",
                "challenge": "",
                "solution": "",
                "results": [],
                "testimonial": "",
            }


case_study_generator_service = CaseStudyGeneratorService()