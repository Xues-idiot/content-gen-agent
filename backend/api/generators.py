"""
Vox Generators API

统一调用所有内容生成服务的 REST API 接口
支持动态服务发现和调用
"""

import os
import uuid
import importlib
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.logging_config import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/api/generators", tags=["generators"])


class GeneratorRequest(BaseModel):
    """通用生成器请求"""
    service_name: str = Field(..., description="服务名称（不含 Generator 后缀）")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="服务参数")


class GeneratorResponse(BaseModel):
    """通用生成器响应"""
    success: bool
    service_name: str
    result: Dict[str, Any]
    error: str = ""


class ServiceInfo(BaseModel):
    """服务信息"""
    name: str
    description: str
    parameters: List[Dict[str, Any]] = []


class ServiceListResponse(BaseModel):
    """服务列表响应"""
    services: List[ServiceInfo]
    total: int


# 服务注册表 - 手动维护服务名称到模块路径的映射
SERVICE_REGISTRY = {
    # 营销活动类
    "linkedin_ad_campaign": "backend.services.linkedin_ad_campaign_generator",
    "twitter_thread": "backend.services.twitter_thread_generator",
    "email_drip_campaign": "backend.services.email_drip_campaign_generator",
    "product_comparison": "backend.services.product_comparison_generator",
    "seasonal_email_campaign": "backend.services.seasonal_email_campaign_generator",
    "webinar_series": "backend.services.webinar_series_generator",
    "brand_partnership_proposal": "backend.services.brand_partnership_proposal_generator",
    "retargeting_ads": "backend.services.retargeting_ads_generator",
    "demand_generation_campaign": "backend.services.demand_generation_campaign_generator",
    "influencer_marketing_strategy": "backend.services.influencer_marketing_strategy_generator",
    "video_marketing_campaign": "backend.services.video_marketing_campaign_generator",

    # 客户管理类
    "customer_feedback_request": "backend.services.customer_feedback_request_generator",
    "customer_onboarding_checklist": "backend.services.customer_onboarding_checklist_generator",
    "client_checklist": "backend.services.client_checklist_generator",
    "client_intake_form": "backend.services.client_intake_form_generator",
    "client_welcome_package": "backend.services.client_welcome_package_generator",
    "loyalty_program_launch": "backend.services.loyalty_program_launch_generator",
    "churn_risk_alert": "backend.services.churn_risk_alert_generator",
    "account_review_template": "backend.services.account_review_template_generator",
    "business_review_presentation": "backend.services.business_review_presentation_generator",
    "ideal_customer_profile": "backend.services.ideal_customer_profile_generator",
    "competitive_positioning_statement": "backend.services.competitive_positioning_statement_generator",

    # 销售支持类
    "roi_calculator": "backend.services.roi_calculator_generator",
    "client_health_score": "backend.services.client_health_score_generator",
    "upsell_recommendation": "backend.services.upsell_recommendation_generator",
    "customer_loyalty_assessment": "backend.services.customer_loyalty_assessment_generator",
    "cross_sell_opportunity": "backend.services.cross_sell_opportunity_generator",
    "contract_renewal_analysis": "backend.services.contract_renewal_analysis_generator",
    "sales_forecast": "backend.services.sales_forecast_generator",
    "territory_planning": "backend.services.territory_planning_generator",
    "price_quote": "backend.services.price_quote_generator",
    "sales_ramp_plan": "backend.services.sales_ramp_plan_generator",
    "account_based_marketing": "backend.services.account_based_marketing_generator",
    "lead_scoring_model": "backend.services.lead_scoring_model_generator",
    "sales_playbook": "backend.services.sales_playbook_generator",
    "competitive_intelligence_report": "backend.services.competitive_intelligence_report_generator",
    "product_launch_plan": "backend.services.product_launch_plan_generator",
    "pricing_strategy": "backend.services.pricing_strategy_generator",
    "customer_success_plan": "backend.services.customer_success_plan_generator",
    "partnership_proposal": "backend.services.partnership_proposal_generator",
    "market_segment_analysis": "backend.services.market_segment_analysis_generator",
    "go_to_market_strategy": "backend.services.go_to_market_strategy_generator",

    # 商业分析类
    "win_loss_analysis": "backend.services.win_loss_analysis_generator",
    "customer_journey_map": "backend.services.customer_journey_map_generator",
    "value_proposition_canvas": "backend.services.value_proposition_canvas_generator",
    "sales_qualification_framework": "backend.services.sales_qualification_framework_generator",
    "account_discovery_report": "backend.services.account_discovery_report_generator",
    "deal_approval_package": "backend.services.deal_approval_package_generator",
    "demo_effectiveness_evaluation": "backend.services.demo_effectiveness_evaluation_generator",
    "sales_training_module": "backend.services.sales_training_module_generator",
    "objection_handling_guide": "backend.services.objection_handling_guide_generator",
    "negotiation_script": "backend.services.negotiation_script_generator",
    "customer_feedback_analysis": "backend.services.customer_feedback_analysis_generator",
    "churn_prediction_model": "backend.services.churn_prediction_model_generator",
    "revenue_forecast_model": "backend.services.revenue_forecast_model_generator",
    "product_pricing_analysis": "backend.services.product_pricing_analysis_generator",
    "customer_profitability_analysis": "backend.services.customer_profitability_analysis_generator",
    "sales_pipeline_review": "backend.services.sales_pipeline_review_generator",
    "key_account_plan": "backend.services.key_account_plan_generator",
    "team_performance_review": "backend.services.team_performance_review_generator",
    "competitive_landscape_analysis": "backend.services.competitive_landscape_analysis_generator",
    "market_growth_strategy": "backend.services.market_growth_strategy_generator",
    "product_roadmap_input": "backend.services.product_roadmap_input_generator",
    "customer_success_metrics": "backend.services.customer_success_metrics_generator",
    "service_expansion_plan": "backend.services.service_expansion_plan_generator",
    "market_entry_analysis": "backend.services.market_entry_analysis_generator",

    # 企业运营类
    "business_model_canvas": "backend.services.business_model_canvas_generator",
    "strategic_partnership_assessment": "backend.services.strategic_partnership_assessment_generator",
    "innovation_opportunity": "backend.services.innovation_opportunity_generator",
    "operational_efficiency_report": "backend.services.operational_efficiency_report_generator",
    "digital_transformation_roadmap": "backend.services.digital_transformation_roadmap_generator",
    "customer_experience_map": "backend.services.customer_experience_map_generator",
    "technology_stack_assessment": "backend.services.technology_stack_assessment_generator",
    "data_governance_framework": "backend.services.data_governance_framework_generator",
    "cybersecurity_strategy": "backend.services.cybersecurity_strategy_generator",
    "enterprise_software_selection": "backend.services.enterprise_software_selection_generator",
    "project_charter": "backend.services.project_charter_generator",
    "agile_sprint_planning": "backend.services.agile_sprint_planning_generator",
    "quality_assurance_plan": "backend.services.quality_assurance_plan_generator",
    "change_management_plan": "backend.services.change_management_plan_generator",
    "business_continuity_plan": "backend.services.business_continuity_plan_generator",
    "it_infrastructure_plan": "backend.services.it_infrastructure_plan_generator",
    "software_development_plan": "backend.services.software_development_plan_generator",

    # 内容与文档类
    "knowledge_base_article": "backend.services.knowledge_base_article_generator",
    "training_materials": "backend.services.training_materials_generator",
    "process_documentation": "backend.services.process_documentation_generator",
    "incident_report": "backend.services.incident_report_generator",
    "performance_dashboard_spec": "backend.services.performance_dashboard_spec_generator",
    "product_backlog": "backend.services.product_backlog_generator",
    "service_level_agreement": "backend.services.service_level_agreement_generator",
    "vendor_risk_assessment": "backend.services.vendor_risk_assessment_generator",
    "api_documentation": "backend.services.api_documentation_generator",
    "user_persona": "backend.services.user_persona_generator",
    "ux_research_plan": "backend.services.ux_research_plan_generator",
    "accessibility_compliance": "backend.services.accessibility_compliance_generator",
    "compliance_audit_checklist": "backend.services.compliance_audit_checklist_generator",
    "data_privacy_impact_assessment": "backend.services.data_privacy_impact_assessment_generator",

    # 营销分析类
    "marketing_analytics_report": "backend.services.marketing_analytics_report_generator",
    "social_media_content_strategy": "backend.services.social_media_content_strategy_generator",
    "email_marketing_automation": "backend.services.email_marketing_automation_generator",
    "content_distribution_strategy": "backend.services.content_distribution_strategy_generator",
    "conversion_rate_optimization": "backend.services.conversion_rate_optimization_generator",
    "marketing_budget_allocation": "backend.services.marketing_budget_allocation_generator",
    "marketing_qualified_lead": "backend.services.marketing_qualified_lead_generator",

    # 其他
    "service_announcement": "backend.services.service_announcement_generator",
    "conversion_optimization": "backend.services.conversion_optimization_generator",
    "brand_voice_guidelines": "backend.services.brand_voice_guidelines_generator",
    "sms_coupon": "backend.services.sms_coupon_generator",
    "crisis_response_plan": "backend.services.crisis_response_plan_generator",
}


def get_service_instance(service_name: str):
    """动态获取服务实例"""
    if service_name not in SERVICE_REGISTRY:
        raise ValueError(f"Service '{service_name}' not found in registry")

    module_path = SERVICE_REGISTRY[service_name]
    try:
        module = importlib.import_module(module_path)
        # 查找服务实例 - 通常是 {service_name}_generator_service
        service_instance_name = f"{service_name.replace('_', '')}_generator_service"
        # 查找 module-level 的服务实例
        for attr_name in dir(module):
            if attr_name.endswith('_generator_service'):
                return getattr(module, attr_name)
        raise ValueError(f"Service instance not found in {module_path}")
    except ImportError as e:
        raise ValueError(f"Failed to import service module: {e}")


@router.get("/", response_model=ServiceListResponse)
async def list_services():
    """列出所有可用的生成服务"""
    services = []
    for name in sorted(SERVICE_REGISTRY.keys()):
        services.append(ServiceInfo(
            name=name,
            description=f"{name.replace('_', ' ').title()} Generator"
        ))
    return ServiceListResponse(services=services, total=len(services))


@router.post("/generate", response_model=GeneratorResponse)
async def generate(request: GeneratorRequest):
    """调用指定的生成服务"""
    try:
        service_name = request.service_name
        parameters = request.parameters

        # 获取服务实例
        service = get_service_instance(service_name)

        # 动态调用生成方法
        # 假设所有服务都有 generate_xxx 方法
        method_name = f"generate_{service_name.replace('-', '_')}"
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            result = await method(**parameters)
        else:
            # 尝试通用 generate 方法
            if hasattr(service, 'generate'):
                result = await service.generate(**parameters)
            else:
                raise ValueError(f"Service {service_name} has no generate method")

        return GeneratorResponse(
            success=True,
            service_name=service_name,
            result=result
        )

    except ValueError as e:
        logger.warning(f"Service not found: {request.service_name}")
        return GeneratorResponse(
            success=False,
            service_name=request.service_name,
            result={},
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Generator error: {e}")
        return GeneratorResponse(
            success=False,
            service_name=request.service_name,
            result={},
            error=f"Internal error: {str(e)}"
        )


@router.get("/{service_name}")
async def get_service_info(service_name: str):
    """获取指定服务的信息"""
    if service_name not in SERVICE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    return {
        "name": service_name,
        "module": SERVICE_REGISTRY[service_name],
        "description": f"{service_name.replace('_', ' ').title()} Generator"
    }
