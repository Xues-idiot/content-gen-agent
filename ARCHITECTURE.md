# Vox (内容生成Agent) - 架构文档

## 项目概述

Vox 是一个垂直领域的内容生成 Agent，专注于**文案+配图**的组合输出，服务于小红书、抖音、公众号、朋友圈等多平台营销内容生成。

---

## 模块架构

```
backend/
├── agents/           # Agent 模块
│   ├── planner.py    # 内容规划
│   ├── copywriter.py # 文案生成
│   ├── reviewer.py   # 内容审核
│   └── exporter.py   # 导出
├── api/              # API 接口
├── prompts/          # Prompt 模板
├── services/         # 服务模块 (LLM)
├── tools/            # 工具模块 (图像、网页搜索)
└── graph/            # 工作流编排
```

---

## planner 模块

### 类型
- `ProductInfo` - 产品信息
  - `name: str` - 产品名称
  - `description: str` - 产品描述
  - `selling_points: List[str]` - 卖点列表
  - `target_users: List[str]` - 目标用户
  - `category: str` - 产品类别
  - `price_range: str` - 价格区间

- `UserProfile` - 用户画像
  - `occupation: str` - 职业
  - `pain_points: List[str]` - 痛点
  - `buying_motivations: List[str]` - 购买动机

- `ContentPlan` - 内容规划
  - `product: ProductInfo`
  - `target_users: List[UserProfile]`
  - `content_direction: str` - 内容方向
  - `key_themes: List[str]` - 主题
  - `tone_of_voice: str` - 语调
  - `recommended_platforms: List[str]` - 推荐平台
  - `content_ratio: dict` - 内容比例
  - `market_insights: List[str]` - 市场洞察
  - `trend_topics: List[str]` - 趋势话题
  - `competitor_content: List[Dict]` - 竞品内容

### 函数
- `plan_content(product: ProductInfo, platforms: List[str], enable_research: bool) -> ContentPlan` - 规划内容方向（集成 Tavily 市场调研）
- `analyze_target_user(product: ProductInfo) -> List[UserProfile]` - 分析目标用户

---

## copywriter 模块

### 类型
- `Platform` (Enum) - 目标平台
  - `XIAOHONGSHU = "xiaohongshu"`
  - `TIKTOK = "tiktok"`
  - `OFFICIAL = "official"`
  - `FRIEND_CIRCLE = "friend_circle"`

- `CopyResult` - 文案结果
  - `platform: str`
  - `title: str`
  - `content: str`
  - `script: str` - 口播脚本（抖音）
  - `tags: List[str]` - 话题标签
  - `image_suggestions: List[str]` - 配图建议
  - `analysis: Dict[str, Any]`
  - `success: bool`
  - `error: str`

### 函数
- `generate(product: ProductInfo, plan: ContentPlan, platform: Platform) -> CopyResult` - 生成单平台文案
- `generate_all(product: ProductInfo, plan: ContentPlan) -> Dict[Platform, CopyResult]` - 生成所有平台文案
- `write_xiaohongshu(product, plan, user_profile) -> CopyResult` - 小红书文案
- `write_tiktok(product, plan, user_profile) -> CopyResult` - 抖音文案
- `write_official(product, plan, user_profile) -> CopyResult` - 公众号文案
- `write_friend_circle(product, plan, user_profile) -> CopyResult` - 朋友圈文案

### Prompt 模板
- `backend/prompts/xiaohongshu.py` - 小红书 Prompt
- `backend/prompts/tiktok.py` - 抖音 Prompt
- `backend/prompts/official.py` - 公众号 Prompt
- `backend/prompts/friend.py` - 朋友圈 Prompt

---

## reviewer 模块

### 类型
- `Violation` - 违规项
  - `word: str` - 违规词
  - `position: int` - 位置
  - `suggestion: str` - 替换建议
  - `severity: str` - 严重程度 (error/warning/info)
  - `category: str` - 违规分类 (最高级/绝对化/虚假夸大)

- `ReviewResult` - 审核结果
  - `passed: bool` - 是否通过
  - `violations: List[Violation]`
  - `quality_score: float` - 0-10
  - `suggestions: List[str]` - 改进建议
  - `analysis: Dict` - 结构分析 (emoji/数字/标签检测)
  - `word_count: int` - 字数
  - `char_count: int` - 字符数

### 变量
- `AD_VIOLATION_WORDS: Dict[str, List[str]]` - 广告法违规词分类字典
- `ALL_VIOLATION_WORDS: List[str]` - 展平后的违规词列表

### 函数
- `check_ad_words(copy: str) -> List[Violation]` - 检测广告法违规词
- `review_quality(copy: str) -> ReviewResult` - 文案质量审核
- `analyze_structure(copy: str) -> Dict` - 分析文案结构
- `batch_review(copies: List[str]) -> List[ReviewResult]` - 批量审核

---

## exporter 模块

### 类型
- `ExportFormat` (Enum)
  - `JSON = "json"`
  - `MARKDOWN = "markdown"`
  - `HTML = "html"`
  - `TEXT = "text"`

- `ExportResult` - 导出结果
  - `success: bool`
  - `content: str`
  - `file_path: str`
  - `error: str`

### 函数
- `export(content: Dict, format: ExportFormat) -> ExportResult` - 导出
- `export_json(content: Dict) -> ExportResult`
- `export_markdown(content: Dict) -> ExportResult`
- `export_html(content: Dict) -> ExportResult`
- `export_text(content: Dict) -> ExportResult`

---

## image-generator 模块

### 类型
- `ImageStyle` (Enum)
  - `MODERN = "modern"`
  - `MINIMAL = "minimal"`
  - `LIFESTYLE = "lifestyle"`
  - `PRODUCT = "product"`
  - `COMPARISON = "comparison"`

- `ImageResult` - 图片结果
- `ImageSuggestion` - 图片建议
  - `type: str` - 图片类型
  - `description: str` - 描述
  - `prompt: str` - 生成 prompt
  - `style: ImageStyle`

### 函数
- `generate_image(prompt: str, style: str, size: str) -> ImageResult` - DALL-E/MJ生成
- `suggest_images(product_name: str, category: str, platform: str) -> List[ImageSuggestion]` - 推荐图片
- `search_stock_images(keyword: str, count: int) -> List[str]` - 搜索素材库

---

## web-search 模块 (Tavily)

### 类型
- `SearchResult` - 搜索结果
  - `title: str` - 标题
  - `url: str` - URL
  - `content: str` - 内容摘要
  - `score: float` - 相关性分数
  - `published_date: Optional[str]` - 发布日期

- `SearchResponse` - 搜索响应
  - `success: bool` - 是否成功
  - `results: List[SearchResult]` - 结果列表
  - `query: str` - 查询关键词
  - `error: Optional[str]` - 错误信息

### 函数
- `search(query, max_results, search_depth) -> SearchResponse` - 关键词搜索
- `search_for_content_inspiration(product_name, category, platform) -> SearchResponse` - 内容灵感搜索
- `search_for_trends(category) -> SearchResponse` - 行业趋势搜索
- `search_for_comp分析(competitor_name) -> SearchResponse` - 竞品分析搜索

---

## content-graph 模块

### 类型
- `WorkflowState` (Enum) - 工作流状态
  - `IDLE`, `PLANNING`, `WRITING`, `REVIEWING`, `GENERATING_IMAGES`, `EXPORTING`, `COMPLETED`, `FAILED`

- `ContentState` - 内容生成状态
  - 产品信息字段
  - `state: WorkflowState`
  - `progress: float` - 0-100
  - `content_plan: Dict`
  - `copy_results: Dict`
  - `review_results: Dict`
  - `image_suggestions: Dict`
  - `final_content: Dict`
  - `errors: List[str]`

### 函数
- `ContentGraph.run(product_info: Dict) -> ContentState` - 运行完整流程
- `ContentGraph.reset()` - 重置状态

### 工作流程
```
1. PLANNING (10%) - 规划内容方向
2. WRITING (40%) - 生成各平台文案
3. REVIEWING (60%) - 审核文案质量
4. GENERATING_IMAGES (80%) - 生成配图建议
5. EXPORTING (90%) - 导出最终结果
6. COMPLETED (100%)
```

---

## api 模块

### 端点
- `POST /api/v1/content/generate` - 生成内容 (限流: 10次/分钟)
- `POST /api/v1/content/review` - 审核文案
- `GET /api/v1/platforms` - 获取平台列表
- `GET /health` - 健康检查
- `GET /` - 根路径

### 中间件
- CORS - 跨域资源共享
- Rate Limiter (slowapi) - 请求限流

### 请求/响应模型
- `ProductInput` - 产品输入 (含 Field 验证)
- `ContentRequest` - 内容请求
- `CopyResultModel` - 文案结果
- `ContentResponse` - 内容响应
- `ReviewResultModel` - 审核结果
- `ViolationModel` - 违规词模型
- `HealthResponse` - 健康检查响应
- `PlatformsResponse` - 平台列表响应

---

## services/llm 模块

### 类型
- `LLMClient` - LLM 客户端

### 装饰器
- `@retry_on_error(max_retries, delay, backoff)` - 指数退避重试

### 函数
- `generate(prompt: str, max_tokens: int, temperature: float, system: str) -> str`
- `generate_with_messages(messages: List[Dict], ...) -> str`
- `parse_structured_output(text: str, format_hint: str) -> Dict`
- `validate_config() -> bool` - 验证 API 配置

### 特性
- 自动重试（指数退避）
- 60秒超时
- Rate limit 和 API error 处理

---

*架构文档 | Vox | 2026-03-24 | 更新于 2026-03-24*
