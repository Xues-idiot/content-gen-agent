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
├── services/         # 服务模块
│   ├── llm.py       # LLM 客户端
│   ├── voice.py     # 语音合成
│   └── subtitle.py   # 字幕生成
├── tools/            # 工具模块
│   ├── image_gen.py       # 图片生成
│   ├── video_generator.py # 视频生成
│   ├── material_collector.py # 素材收集
│   └── web_search.py      # 网页搜索
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

## video-generator 模块 (基于 MoneyPrinterTurbo)

### 类型
- `VideoAspect` (Enum) - 视频比例
  - `PORTRAIT = "9:16"` - 竖屏 1080x1920
  - `LANDSCAPE = "16:9"` - 横屏 1920x1080
  - `SQUARE = "1:1"` - 方屏 1080x1080

- `VideoConcatMode` (Enum) - 视频拼接模式
  - `RANDOM = "random"` - 随机
  - `SEQUENTIAL = "sequential"` - 顺序

- `VideoTransitionMode` (Enum) - 视频转场模式
  - `NONE = "none"` - 无转场
  - `FADE_IN = "fade_in"` - 淡入
  - `FADE_OUT = "fade_out"` - 淡出
  - `SLIDE_IN = "slide_in"` - 滑入
  - `SLIDE_OUT = "slide_out"` - 滑出
  - `SHUFFLE = "shuffle"` - 随机

- `VideoParams` - 视频参数
  - `video_aspect: VideoAspect` - 视频比例
  - `video_concat_mode: VideoConcatMode` - 拼接模式
  - `video_transition_mode: VideoTransitionMode` - 转场模式
  - `video_clip_duration: int` - 每个片段最大时长
  - `subtitle_enabled: bool` - 是否启用字幕
  - `bgm_type: str` - 背景音乐类型
  - `voice_name: str` - 语音名称

- `VideoResult` - 视频生成结果
  - `video_path: str` - 视频文件路径
  - `audio_path: str` - 音频文件路径
  - `subtitle_path: str` - 字幕文件路径
  - `duration: float` - 时长
  - `success: bool`
  - `error: str`

### 类：VideoGenerator
- `combine_videos(video_paths, audio_path, output_path, params) -> str` - 拼接多个视频
- `generate_video(video_path, audio_path, subtitle_path, output_path, params) -> VideoResult` - 生成最终视频
- `preprocess_video_materials(materials, clip_duration) -> List[MaterialInfo]` - 预处理视频素材

---

## material-collector 模块

### 类型
- `MaterialInfo` - 素材信息
  - `provider: str` - 来源 (pexels/pixabay/local)
  - `url: str` - 素材URL
  - `duration: float` - 时长
  - `width: int` - 宽度
  - `height: int` - 高度

- `MaterialCollection` - 素材收集结果
  - `materials: List[MaterialInfo]`
  - `total_duration: float`
  - `success: bool`

### 类：MaterialCollector
- `search_videos_pexels(search_term, video_aspect, per_page) -> List[dict]` - 搜索 Pexels 视频
- `search_videos_pixabay(search_term, video_aspect, per_page) -> List[dict]` - 搜索 Pixabay 视频
- `search_videos(search_term, video_aspect, source) -> List[dict]` - 统一搜索接口
- `download_video(video_url, save_dir) -> str` - 下载单个视频
- `download_videos(search_terms, video_aspect, source, audio_duration) -> List[str]` - 批量下载视频

---

## voice 模块 (语音合成)

### 类：VoiceService
- `generate_audio(text, voice_name, voice_rate, output_path) -> Tuple[str, float]` - 生成 TTS 音频
- `generate_with_subtitles(text, voice_name, voice_rate, output_dir) -> Tuple[audio_path, subtitle_path, duration]` - 生成音频和字幕
- `get_available_voices() -> List[Dict]` - 获取可用声音列表

### 支持的声音
- Edge TTS (微软，免费，推荐)
- 中文女声：zh-CN-XiaoxiaoNeural, zh-CN-XiaoyiNeural
- 中文男声：zh-CN-YunxiNeural, zh-CN-YunyangNeural
- 粤语女声：zh-HK-HiuGaaiNeural
- 更多声音见 `backend/services/voice.py`

---

## subtitle 模块 (字幕生成)

### 类：SubtitleService
- `generate_subtitle(audio_path, output_path, language) -> str` - 使用 Whisper 生成字幕
- `correct_subtitle(subtitle_path, original_script) -> bool` - 校正字幕文件
- `parse_srt(path) -> List[Dict]` - 解析 SRT 文件

### 功能
- Whisper 语音识别生成字幕
- Levenshtein 距离校正
- SRT 文件解析和生成

---

## video API 端点

### 视频素材
- `POST /api/v1/video/search-materials` - 搜索视频素材
- `POST /api/v1/video/download` - 下载视频

### 视频处理
- `POST /api/v1/video/generate-audio` - 生成语音
- `POST /api/v1/video/generate-subtitle` - 生成字幕
- `POST /api/v1/video/combine` - 合并视频
- `POST /api/v1/video/generate` - 生成最终视频
- `GET /api/v1/video/voices` - 获取可用声音列表

---

## video 前端组件

### VideoGenerator 组件

视频生成完整工作流组件，支持：

- 视频素材搜索（Pexels/Pixabay）
- 语音生成（Edge TTS）
- 字幕生成（Whisper）
- 视频合并与最终视频生成

#### 类型定义

```typescript
// VideoSearchRequest
{
  search_terms: string[];
  video_aspect: string; // "9:16", "16:9", "1:1"
  source: string; // "pexels", "pixabay"
}

// AudioGenerateRequest
{
  text: string;
  voice_name: string;
  voice_rate: number;
}

// VideoGenerateRequest
{
  video_path: string;
  audio_path: string;
  subtitle_path?: string;
  video_aspect: string;
  subtitle_enabled: boolean;
  bgm_type: string;
  bgm_volume: number;
}
```

#### 视频生成流程

1. **搜索素材** - 输入关键词搜索 Pexels/Pixabay 视频
2. **生成语音** - 使用 Edge TTS 将文案转为语音
3. **合并视频** - 将视频片段与音频合并
4. **生成最终视频** - 添加字幕和背景音乐

### API 函数

```typescript
searchVideoMaterials(request: VideoSearchRequest): Promise<VideoSearchResponse>
downloadVideos(request: VideoDownloadRequest): Promise<VideoDownloadResponse>
generateAudio(request: AudioGenerateRequest): Promise<AudioGenerateResponse>
generateSubtitle(request: SubtitleGenerateRequest): Promise<SubtitleGenerateResponse>
combineVideos(request: VideoCombineRequest): Promise<VideoCombineResponse>
generateVideo(request: VideoGenerateRequest): Promise<VideoGenerateResponse>
getAvailableVoices(): Promise<{ success: boolean; voices: Voice[]; total: number }>
```

---

*架构文档 | Vox | 2026-03-24 | 更新于 2026-03-24*
