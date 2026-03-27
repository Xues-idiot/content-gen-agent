"""
Vox Content ROI Calculator Service 模块

内容ROI计算服务
- 计算内容投资回报率
- 成本效益分析
- 优化建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class ROIMetrics:
    """ROI指标"""
    total_cost: float
    estimated_reach: int
    estimated_conversions: int
    estimated_revenue: float
    roi_percentage: float
    cost_per_reach: float
    cost_per_conversion: float


class ContentROICalculatorService:
    """
    内容ROI计算服务

    计算内容的投资回报率
    """

    def __init__(self):
        self.llm = llm_service

    # 估算成本因素
    COST_FACTORS = {
        "creation": {
            "name": "创作成本",
            "description": "内容创作所花时间价值",
            "default_rate": 100,  # 元/小时
        },
        "promotion": {
            "name": "推广成本",
            "description": "付费推广费用",
            "default_rate": 0,  # 按实际
        },
        "production": {
            "name": "制作成本",
            "description": "素材、设备等制作费用",
            "default_rate": 0,  # 按实际
        },
    }

    # 平均转化价值估算
    AVERAGE_CONVERSION_VALUES = {
        "xiaohongshu": {
            "follow": 0.5,  # 元/粉丝
            "click": 1.0,  # 元/点击
            "purchase": 50.0,  # 元/购买
        },
        "tiktok": {
            "follow": 0.3,
            "click": 0.8,
            "purchase": 40.0,
        },
        "weibo": {
            "follow": 0.4,
            "click": 1.2,
            "purchase": 60.0,
        },
        "official": {
            "follow": 1.0,
            "click": 2.0,
            "purchase": 100.0,
        },
    }

    async def calculate_roi(
        self,
        content_metrics: Dict[str, Any],
        cost_breakdown: Dict[str, float],
        platform: str = "xiaohongshu",
    ) -> ROIMetrics:
        """
        计算ROI

        Args:
            content_metrics: 内容指标（浏览、点赞、评论、转化等）
            cost_breakdown: 成本明细
            platform: 平台

        Returns:
            ROIMetrics: ROI指标
        """
        # 计算总成本
        total_cost = sum(cost_breakdown.values())

        # 获取指标
        reach = content_metrics.get("reach", content_metrics.get("views", 0))
        likes = content_metrics.get("likes", 0)
        comments = content_metrics.get("comments", 0)
        shares = content_metrics.get("shares", 0)
        conversions = content_metrics.get("conversions", 0)

        # 估算影响价值
        engagement_value = (likes * 0.1 + comments * 0.5 + shares * 1.0)
        awareness_value = reach * 0.01  # 每曝光价值0.01元

        # 估算收入
        conv_value = self.AVERAGE_CONVERSION_VALUES.get(
            platform, self.AVERAGE_CONVERSION_VALUES["xiaohongshu"]
        )
        estimated_revenue = (conversions * conv_value.get("purchase", 50) +
                           reach * 0.01 + engagement_value)

        # 计算ROI
        if total_cost > 0:
            roi_percentage = ((estimated_revenue - total_cost) / total_cost) * 100
        else:
            roi_percentage = 0

        # 计算单位成本
        cost_per_reach = total_cost / reach if reach > 0 else 0
        cost_per_conversion = total_cost / conversions if conversions > 0 else 0

        return ROIMetrics(
            total_cost=total_cost,
            estimated_reach=reach,
            estimated_conversions=conversions,
            estimated_revenue=estimated_revenue,
            roi_percentage=roi_percentage,
            cost_per_reach=cost_per_reach,
            cost_per_conversion=cost_per_conversion,
        )

    async def estimate_potential(
        self,
        content_type: str,
        platform: str = "xiaohongshu",
        budget: float = 1000,
    ) -> Dict[str, Any]:
        """
        估算潜力

        Args:
            content_type: 内容类型
            platform: 平台
            budget: 预算

        Returns:
            Dict: 潜力估算
        """
        try:
            prompt = f"""请估算以下类型内容的潜力。

内容类型：{content_type}
平台：{platform}
预算：{budget}元

请估算：
1. 预计浏览量范围
2. 预计互动量
3. 预计转化数
4. 建议预算分配

请以JSON格式返回：
{{
    "reach_range": {{"min": 1000, "max": 5000}},
    "engagement_estimate": {{"likes": 100, "comments": 20}},
    "conversion_estimate": 10,
    "budget_allocation": {{"创作": 500, "推广": 500}}
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "content_type": content_type,
                "platform": platform,
                "budget": budget,
                **result,
            }

        except Exception as e:
            logger.error(f"估算潜力失败: {e}")
            return {
                "content_type": content_type,
                "platform": platform,
                "budget": budget,
                "reach_range": {"min": 0, "max": 0},
                "engagement_estimate": {"likes": 0, "comments": 0},
                "conversion_estimate": 0,
                "budget_allocation": {},
            }

    def get_cost_factors(self) -> Dict[str, Any]:
        """
        获取成本因素

        Returns:
            Dict: 成本因素列表
        """
        return self.COST_FACTORS


# 全局实例
content_roi_calculator_service = ContentROICalculatorService()


if __name__ == "__main__":
    import asyncio

    service = ContentROICalculatorService()

    async def test():
        print("=== ROI计算 ===")
        metrics = {
            "reach": 10000,
            "likes": 500,
            "comments": 50,
            "shares": 20,
            "conversions": 10,
        }
        costs = {"creation": 500, "promotion": 200}

        roi = await service.calculate_roi(metrics, costs, "xiaohongshu")
        print(f"总成本: {roi.total_cost}元")
        print(f"预估收入: {roi.estimated_revenue}元")
        print(f"ROI: {roi.roi_percentage}%")
        print(f"单次触达成本: {roi.cost_per_reach:.4f}元")

        print("\n=== 潜力估算 ===")
        potential = await service.estimate_potential("测评", "xiaohongshu", 1000)
        print(f"浏览量: {potential['reach_range']}")

    asyncio.run(test())