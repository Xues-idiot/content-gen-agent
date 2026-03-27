"""
Vox Service Level Agreement Generator Service 模块

服务水平协议生成服务
- 服务承诺
- 指标定义
- 赔偿条款
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ServiceLevelAgreementGeneratorService:
    """
    服务水平协议生成服务

    生成服务水平协议内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sla(
        self,
        service_name: str,
        service_type: str = "SaaS",
        tier: str = "standard",
    ) -> Dict[str, Any]:
        """
        生成服务水平协议

        Args:
            service_name: 服务名称
            service_type: 服务类型
            tier: 服务等级

        Returns:
            Dict: 服务水平协议
        """
        try:
            prompt = f"""请为"{service_name}"（类型：{service_type}，等级：{tier}）生成服务水平协议。

请以JSON格式返回：
{{
    "service_name": "服务名称",
    "service_type": "服务类型",
    "tier": "服务等级",
    "effective_date": "生效日期",
    "overview": "概述",
    "service_availability": {{
        "uptime_guarantee": "可用性保证",
        "measurement_method": "测量方法",
        "exclusions": "排除项"
    }},
    "performance_metrics": [
        {{
            "metric": "指标",
            "target": "目标",
            "measurement": "测量方法"
        }}
    ],
    "response_times": {{
        "critical": "关键响应时间",
        "high": "高优先级响应时间",
        "medium": "中优先级响应时间",
        "low": "低优先级响应时间"
    }},
    "support_availability": "支持可用性",
    "maintenance_windows": "维护窗口",
    "incident_management": "事件管理",
    "credits_and_refunds": "积分与退款",
    "limitations_and_exclusions": ["限制与排除1"],
    "reporting_and_monitoring": "报告与监控",
    "customer_responsibilities": "客户责任",
    "term_and_termination": "条款与终止"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "service_name": service_name,
                "service_type": service_type,
                "tier": tier,
                **result,
            }

        except Exception as e:
            logger.error(f"生成服务水平协议失败: {e}")
            return {
                "service_name": service_name,
                "service_type": service_type,
                "tier": tier,
                "effective_date": "",
                "overview": "",
                "service_availability": {},
                "performance_metrics": [],
                "response_times": {},
                "support_availability": "",
                "maintenance_windows": "",
                "incident_management": "",
                "credits_and_refunds": "",
                "limitations_and_exclusions": [],
                "reporting_and_monitoring": "",
                "customer_responsibilities": "",
                "term_and_termination": "",
            }


service_level_agreement_generator_service = ServiceLevelAgreementGeneratorService()