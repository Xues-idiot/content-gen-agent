# Vox 学习记录

## 学到的知识

### 第1-30轮 实现总结

#### 1. 项目架构设计
- 模块化设计：agents, prompts, services, api, graph, tools
- 数据类 (dataclass) 用于定义类型安全的数据结构
- 枚举 (Enum) 用于限制可选值

#### 2. Prompt 工程
- Role + Goals + Constraints + Context + Output Format 结构
- 小红书：emoji + 悬念开头 + 场景描述 + 标签
- 抖音：3秒钩子 + 短句节奏 + 行动号召
- 公众号：深度内容 + 多级标题 + 数据支撑
- 朋友圈：简短自然 + 生活化场景

#### 3. 审核机制
- 违规词库（广告法敏感词）
- 质量评分算法（基于违规词、长度、结构）
- 替换建议生成

#### 4. 前端设计
- Next.js 14 App Router
- Tailwind CSS 原子化样式
- 组件化设计：ProductInput, PlatformSelect, CopyOutput, ImagePreview, ExportPanel

#### 5. API 设计
- RESTful API
- Request/Response 模型 (Pydantic)
- FastAPI 路由分组

---

## Sigma Skills 应用

- **社交媒体营销**：平台选择策略已应用于 PlatformSelect 组件
- **批判性思维**：违规词检测和逻辑审核已应用于 Reviewer 模块
- **内容营销**：内容比例分配已应用于 Planner 模块
- **Tavily Web Search**：市场调研功能集成（第201轮）

---

## 第201-205轮 新学到的知识

### 1. Tavily API 集成
- Tavily 是一个 LLM 优化的搜索 API
- 支持多搜索深度 (basic/medium/deep)
- 可以获取相关内容摘要和元数据
- 适用于市场调研、竞品分析、趋势研究

### 2. 市场调研工作流
- 在内容规划阶段自动进行市场调研
- 收集行业趋势、竞品内容、市场洞察
- 可以选择性地启用/禁用调研功能
- 调研结果包含 URL 可追溯来源

### 3. 行动号召 (CTA) 设计
- TikTok 文案包含结尾行动号召
- CTA 是用户转化的关键元素
- 可以从 LLM 输出中解析提取 CTA
- 前端单独展示 CTA 以增强可见性

### 4. viral-marketing skill 了解
- 病毒营销关注裂变机制、K因子
- 适合产品冷启动和增长黑客场景
- 核心要素：激励设计、传播路径、防刷机制
- 与内容生成的关联：素材准备（话术设计）

---

## MoneyPrinterTurbo 参考应用

- 多 LLM Provider 模式 → LLMClient 类
- 管道式 start() 函数 → ContentGraph 编排
- 配置管理 → config.py 模块

---

## 待学习

- GitHub 趋势：AI content generation / marketing copy 相关项目
- 实际 API 测试和调优
- 前端状态管理 (Redux/Zustand)
- 端到端测试
