"""
Vox Data Dictionary Generator Service 模块

数据字典生成服务
- 数据定义
- 字段说明
- 类型规范
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DataDictionaryGeneratorService:
    """
    数据字典生成服务

    生成数据字典内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_data_dictionary(
        self,
        database_name: str,
        num_tables: int = 5,
    ) -> Dict[str, Any]:
        """
        生成数据字典

        Args:
            database_name: 数据库名称
            num_tables: 表数量

        Returns:
            Dict: 数据字典
        """
        try:
            prompt = f"""请为"{database_name}"数据库生成包含{num_tables}个表的数据字典。

请以JSON格式返回：
{{
    "database_name": "数据库名称",
    "num_tables": 表数,
    "overview": "概述",
    "tables": [
        {{
            "table_name": "表名",
            "description": "描述",
            "primary_key": "主键",
            "fields": [
                {{
                    "field_name": "字段名",
                    "data_type": "数据类型",
                    "length": "长度",
                    "nullable": "是否可空",
                    "default_value": "默认值",
                    "description": "描述"
                }}
            ],
            "indexes": ["索引1"],
            "foreign_keys": ["外键1"]
        }}
    ],
    "relationships": ["表关系1"],
    "assumptions": ["假设1"],
    "version": "版本"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "database_name": database_name,
                "num_tables": num_tables,
                **result,
            }

        except Exception as e:
            logger.error(f"生成数据字典失败: {e}")
            return {
                "database_name": database_name,
                "num_tables": num_tables,
                "overview": "",
                "tables": [],
                "relationships": [],
                "assumptions": [],
                "version": "",
            }


data_dictionary_generator_service = DataDictionaryGeneratorService()