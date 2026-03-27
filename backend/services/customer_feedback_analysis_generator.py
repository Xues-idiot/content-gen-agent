"""
Vox Customer Feedback Analysis Generator Service 模块

客户反馈分析生成服务
- 反馈主题
- 情感分析
- 行动建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerFeedbackAnalysisGeneratorService:
    """
    客户反馈分析生成服务

    生成客户反馈分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_feedback_analysis(
        self,
        feedback_source: str,
        time_period: str,
        num_themes: int = 8,
    ) -> Dict[str, Any]:
        """
        生成客户反馈分析

        Args:
            feedback_source: 反馈来源
            time_period: 时间周期
            num_themes: 主题数量

        Returns:
            Dict: 客户反馈分析
        """
        try:
            prompt = f"""请为{feedback_source}来源在{time_period}期间的反馈生成{num_themes}个主题的分析。

请以JSON格式返回：
{{
    "feedback_source": "反馈来源",
    "time_period": "时间周期",
    "num_themes": {num_themes},
    "executive_summary": "执行摘要",
    "overall_sentiment": "整体情感",
    "volume_metrics": {{
        "total_feedback": "总反馈数",
        "response_rate": "响应率",
        "trend": "趋势"
    }},
    "theme_analysis": [
        {{
            "theme": "主题",
            "frequency": "频率",
            "sentiment": "情感",
            "key_verbatim": ["关键原话1"]
        }}
    ],
    "positive_highlights": ["正面亮点1"],
    "areas_of_concern": ["关注领域1"],
    "actionable_insights": ["可操作的洞察1"],
    "recommended_priorities": ["推荐优先级1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "feedback_source": feedback_source,
                "time_period": time_period,
                "num_themes": num_themes,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户反馈分析失败: {e}")
            return {
                "feedback_source": feedback_source,
                "time_period": time_period,
                "num_themes": num_themes,
                "executive_summary": "",
                "overall_sentiment": "",
                "volume_metrics": {},
                "theme_analysis": [],
                "positive_highlights": [],
                "areas_of_concern": [],
                "actionable_insights": [],
                "recommended_priorities": [],
            }


customer_feedback_analysis_generator_service = CustomerFeedbackAnalysisGeneratorService()
