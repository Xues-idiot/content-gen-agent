"""
Vox Content Template Generator Service 模块

内容模板生成服务
- 多种内容模板生成
- 模板结构分析
- 个性化模板定制
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class ContentTemplate:
    """内容模板"""
    template_type: str
    title_template: str
    content_structure: str
    required_elements: List[str]
    optional_elements: List[str]
    example: str


class ContentTemplateGeneratorService:
    """
    内容模板生成服务

    生成各种类型的内容模板
    """

    def __init__(self):
        self.llm = llm_service

    # 预置模板类型
    TEMPLATE_TYPES = {
        "开箱测评": {
            "title_patterns": [
                "【{产品名称}】{测评结果}，真实体验分享",
                "{数字}个维度测评{产品名称}，看完再买！",
                "{产品名称}深度测评 | {特色角度}",
            ],
            "structure": "痛点引入→产品介绍→核心测评→对比优势→总结推荐",
            "required": ["产品外观", "使用体验", "效果展示", "真实评价"],
            "optional": ["价格分析", "适用人群", "购买建议"],
        },
        "好物推荐": {
            "title_patterns": [
                "私藏{数字}年！{产品名称}真的绝绝子",
                "{人群}必看！{产品名称}推荐清单",
                "后悔没早点买系列 | {产品名称}",
            ],
            "structure": "个人经历→需求背景→产品推荐→使用感受→总结",
            "required": ["个人体验", "产品亮点", "真实感受"],
            "optional": ["购买渠道", "优惠信息", "注意事项"],
        },
        "教程分享": {
            "title_patterns": [
                "{主题}教程 | {成果}一看就会",
                "新手必看！{主题}完整指南",
                "{数字}分钟学会{主题}，建议收藏",
            ],
            "structure": "问题引入→步骤讲解→难点提示→成果展示→延伸扩展",
            "required": ["步骤清晰", "要点明确", "图文配合"],
            "optional": ["常见错误", "进阶技巧", "资源推荐"],
        },
        "日常分享": {
            "title_patterns": [
                "今日份{心情} | {场景描述}",
                "plog | {时间或场景}的{主题}",
                "记录{主题}的{数字}天",
            ],
            "structure": "场景描述→经历分享→感受表达→互动引导",
            "required": ["生活气息", "真实感", "情感共鸣"],
            "optional": ["拍照技巧", "好物分享", "经验总结"],
        },
        "对比测评": {
            "title_patterns": [
                "{产品A} vs {产品B} | 真实对比测评",
                "{数字}款{品类}横评 | 哪款值得买？",
                "客观测评 | {产品A}和{产品B}怎么选",
            ],
            "structure": "测评背景→产品介绍→多维度对比→优缺点分析→选购建议",
            "required": ["对比维度", "客观数据", "明确结论"],
            "optional": ["价格对比", "适用场景", "购买建议"],
        },
    }

    async def generate_template(
        self,
        template_type: str,
        product_info: Dict[str, Any],
        platform: str = "xiaohongshu",
    ) -> ContentTemplate:
        """
        生成内容模板

        Args:
            template_type: 模板类型
            product_info: 产品信息
            platform: 平台

        Returns:
            ContentTemplate: 内容模板
        """
        try:
            prompt = f"""请为"{template_type}"类型生成内容模板。

平台：{platform}
产品名称：{product_info.get('name', '未知')}
产品描述：{product_info.get('description', '未知')}
产品特点：{', '.join(product_info.get('selling_points', []))}
目标用户：{', '.join(product_info.get('target_users', []))}

请生成：
1. 标题模板（3个不同角度）
2. 内容结构
3. 必备元素
4. 可选元素
5. 示例文案

请以JSON格式返回：
{{
    "template_type": "{template_type}",
    "title_template": "标题模板",
    "content_structure": "内容结构描述",
    "required_elements": ["元素1", "元素2"],
    "optional_elements": ["元素1", "元素2"],
    "example": "示例文案"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            # 如果LLM返回的结果有问题，使用预设模板
            if not result.get("title_template"):
                preset = self.TEMPLATE_TYPES.get(template_type, self.TEMPLATE_TYPES["好物推荐"])
                result = {
                    "template_type": template_type,
                    "title_template": preset["title_patterns"][0],
                    "content_structure": preset["structure"],
                    "required_elements": preset["required"],
                    "optional_elements": preset["optional"],
                    "example": "",
                }

            return ContentTemplate(
                template_type=result.get("template_type", template_type),
                title_template=result.get("title_template", ""),
                content_structure=result.get("content_structure", ""),
                required_elements=result.get("required_elements", []),
                optional_elements=result.get("optional_elements", []),
                example=result.get("example", ""),
            )

        except Exception as e:
            logger.error(f"生成模板失败: {e}")
            preset = self.TEMPLATE_TYPES.get(template_type, self.TEMPLATE_TYPES["好物推荐"])
            return ContentTemplate(
                template_type=template_type,
                title_template=preset["title_patterns"][0],
                content_structure=preset["structure"],
                required_elements=preset["required"],
                optional_elements=preset["optional"],
                example="",
            )

    def get_template_types(self) -> List[str]:
        """
        获取所有模板类型

        Returns:
            List[str]: 模板类型列表
        """
        return list(self.TEMPLATE_TYPES.keys())

    async def suggest_template_for_product(
        self,
        product_info: Dict[str, Any],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        为产品推荐合适的模板类型

        Args:
            product_info: 产品信息
            platform: 平台

        Returns:
            Dict: 推荐结果
        """
        try:
            prompt = f"""请为以下产品推荐最合适的内容模板类型。

平台：{platform}
产品名称：{product_info.get('name', '未知')}
产品描述：{product_info.get('description', '未知')}
产品特点：{', '.join(product_info.get('selling_points', []))}

可选模板类型：{', '.join(self.TEMPLATE_TYPES.keys())}

请分析并推荐：
1. 最适合的模板类型（1-2个）
2. 推荐理由
3. 标题角度建议

请以JSON格式返回：
{{
    "recommended_types": ["类型1", "类型2"],
    "reasons": ["理由1", "理由2"],
    "title_suggestions": ["角度1", "角度2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_info.get("name", ""),
                "platform": platform,
                "recommended_types": result.get("recommended_types", ["好物推荐"]),
                "reasons": result.get("reasons", []),
                "title_suggestions": result.get("title_suggestions", []),
            }

        except Exception as e:
            logger.error(f"推荐模板失败: {e}")
            return {
                "product_name": product_info.get("name", ""),
                "platform": platform,
                "recommended_types": ["好物推荐"],
                "reasons": ["默认推荐"],
                "title_suggestions": [],
            }

    async def customize_template(
        self,
        base_template: str,
        customization: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        定制模板

        Args:
            base_template: 基础模板内容
            customization: 定制需求

        Returns:
            Dict: 定制后的模板
        """
        try:
            prompt = f"""请根据以下需求定制模板。

基础模板：{base_template}

定制需求：
目标受众：{customization.get('target_audience', '通用')}
内容长度：{customization.get('content_length', '中等')}
语气风格：{customization.get('tone_style', '亲切')}
重点突出：{customization.get('focus', '产品特点')}

请提供定制后的：
1. 标题模板
2. 内容结构
3. 写作要点

请以JSON格式返回：
{{
    "customized_title": "定制标题",
    "customized_structure": "定制结构",
    "writing_points": ["要点1", "要点2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "original_template": base_template,
                "customization": customization,
                "customized_title": result.get("customized_title", base_template),
                "customized_structure": result.get("customized_structure", ""),
                "writing_points": result.get("writing_points", []),
            }

        except Exception as e:
            logger.error(f"定制模板失败: {e}")
            return {
                "original_template": base_template,
                "customization": customization,
                "customized_title": base_template,
                "customized_structure": "",
                "writing_points": [],
            }


# 全局实例
content_template_generator_service = ContentTemplateGeneratorService()


if __name__ == "__main__":
    import asyncio

    service = ContentTemplateGeneratorService()

    async def test():
        print("=== 可用模板类型 ===")
        types = service.get_template_types()
        print(f"类型: {', '.join(types)}")

        print("\n=== 生成模板 ===")
        template = await service.generate_template(
            "开箱测评",
            {
                "name": "某品牌面霜",
                "description": "保湿修护面霜",
                "selling_points": ["保湿", "修护", "温和"],
                "target_users": ["干皮", "敏感肌"],
            },
            "xiaohongshu"
        )
        print(f"类型: {template.template_type}")
        print(f"标题: {template.title_template}")
        print(f"结构: {template.content_structure}")
        print(f"必备: {', '.join(template.required_elements[:2])}")

        print("\n=== 推荐模板 ===")
        rec = await service.suggest_template_for_product(
            {
                "name": "某品牌面霜",
                "description": "保湿修护面霜",
                "selling_points": ["保湿", "修护", "温和"],
            },
            "xiaohongshu"
        )
        print(f"推荐: {', '.join(rec['recommended_types'])}")
        print(f"理由: {', '.join(rec['reasons'][:2])}")

    asyncio.run(test())