"""
Vox 验证模块

提供请求验证和数据验证功能
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationError:
    """验证错误"""
    field: str
    message: str


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[ValidationError] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    @property
    def error_messages(self) -> List[str]:
        return [f"{e.field}: {e.message}" for e in self.errors]


class ProductValidator:
    """产品信息验证器"""

    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 100
    MIN_DESCRIPTION_LENGTH = 1
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_SELLING_POINTS = 20
    MAX_TARGET_USERS = 20

    def validate(
        self,
        name: str,
        description: str,
        selling_points: List[str] = None,
        target_users: List[str] = None,
        category: str = "",
        price_range: str = "",
    ) -> ValidationResult:
        """
        验证产品信息

        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        selling_points = selling_points or []
        target_users = target_users or []

        # 验证产品名称
        if not name or not name.strip():
            errors.append(ValidationError("name", "产品名称不能为空"))
        elif len(name) > self.MAX_NAME_LENGTH:
            errors.append(ValidationError("name", f"产品名称不能超过{self.MAX_NAME_LENGTH}个字符"))
        elif len(name) < self.MIN_NAME_LENGTH:
            errors.append(ValidationError("name", f"产品名称至少需要{self.MIN_NAME_LENGTH}个字符"))

        # 验证产品描述
        if not description or not description.strip():
            errors.append(ValidationError("description", "产品描述不能为空"))
        elif len(description) > self.MAX_DESCRIPTION_LENGTH:
            errors.append(ValidationError("description", f"产品描述不能超过{self.MAX_DESCRIPTION_LENGTH}个字符"))

        # 验证卖点列表
        if len(selling_points) > self.MAX_SELLING_POINTS:
            errors.append(ValidationError("selling_points", f"卖点数量不能超过{self.MAX_SELLING_POINTS}个"))

        for i, point in enumerate(selling_points):
            if len(point) > 100:
                errors.append(ValidationError(f"selling_points[{i}]", "单个卖点不能超过100个字符"))
                break

        # 验证目标用户列表
        if len(target_users) > self.MAX_TARGET_USERS:
            errors.append(ValidationError("target_users", f"目标用户数量不能超过{self.MAX_TARGET_USERS}个"))

        for i, user in enumerate(target_users):
            if len(user) > 50:
                errors.append(ValidationError(f"target_users[{i}]", "单个目标用户不能超过50个字符"))
                break

        # 验证类别
        valid_categories = ["美妆", "数码", "食品", "家居", "服装", "健康", "教育", "旅游", "其他", ""]
        if category and category not in valid_categories:
            errors.append(ValidationError("category", f"无效的产品类别: {category}"))

        # 验证价格区间
        if price_range and len(price_range) > 50:
            errors.append(ValidationError("price_range", "价格区间不能超过50个字符"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)


class PlatformValidator:
    """平台验证器"""

    VALID_PLATFORMS = {"xiaohongshu", "tiktok", "official", "friend_circle"}

    def validate(self, platforms: List[str]) -> ValidationResult:
        """
        验证平台列表

        Returns:
            ValidationResult: 验证结果
        """
        errors = []

        if not platforms:
            errors.append(ValidationError("platforms", "至少需要选择一个平台"))
            return ValidationResult(is_valid=False, errors=errors)

        invalid_platforms = set(platforms) - self.VALID_PLATFORMS
        if invalid_platforms:
            errors.append(ValidationError(
                "platforms",
                f"无效的平台: {', '.join(invalid_platforms)}"
            ))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)


class ContentValidator:
    """内容验证器"""

    MIN_COPY_LENGTH = 10
    MAX_COPY_LENGTH = 10000

    def validate_copy(self, content: str) -> ValidationResult:
        """
        验证文案内容

        Returns:
            ValidationResult: 验证结果
        """
        errors = []

        if not content:
            errors.append(ValidationError("content", "文案内容不能为空"))
            return ValidationResult(is_valid=False, errors=errors)

        length = len(content)
        if length < self.MIN_COPY_LENGTH:
            errors.append(ValidationError("content", f"文案内容至少需要{self.MIN_COPY_LENGTH}个字符"))
        elif length > self.MAX_COPY_LENGTH:
            errors.append(ValidationError("content", f"文案内容不能超过{self.MAX_COPY_LENGTH}个字符"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_enable_research(self, enable_research: bool) -> ValidationResult:
        """
        验证市场调研开关

        Returns:
            ValidationResult: 验证结果
        """
        errors = []

        if not isinstance(enable_research, bool):
            errors.append(ValidationError("enable_research", "enable_research 必须是布尔值"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)


# 全局验证器实例
product_validator = ProductValidator()
platform_validator = PlatformValidator()
content_validator = ContentValidator()


if __name__ == "__main__":
    # 测试
    result = product_validator.validate(
        name="智能睡眠枕",
        description="AI智能枕头",
        selling_points=["改善睡眠"],
        target_users=["失眠人群"],
        category="家居",
    )
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.error_messages}")

    # 测试无效数据
    result = product_validator.validate(
        name="",
        description="",
        selling_points=[],
        target_users=[],
    )
    print(f"\nInvalid test:")
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.error_messages}")
