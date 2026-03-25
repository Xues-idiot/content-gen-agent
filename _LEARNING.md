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

---

## 第414轮 GitHub Push 阻止问题

### 问题描述
- 初始提交 `4192e797` 包含真实的 API keys 和 GitHub token
- GitHub secret scanning 检测到并阻止 push
- 错误信息: `GH013: Repository rule violations found`

### 解决方案
1. **临时方案（已执行）**: 替换 `INSTRUCTIONS.md` 中的 secrets 为占位符
2. **长期方案**: 用户需访问 unblock URL 解除阻止
   - URL: `https://github.com/Xues-idiot/content-gen-agent/security/secret-scanning/unblock-secret/3BQD3HM877GijaLJe4c7NLdEqSe`

### 经验教训
1. **永远不要在代码库中存储真实 secrets** - 即使是文档文件
2. **使用 .gitignore 和环境变量** - 不提交 .env 文件
3. **文档中的 secrets 占位符** - 示例使用 `your_api_key_here`

### GitHub Token 配置
- Token 已设置在 remote URL（但 push 时被阻止）
- Repo: `Xues-idiot/content-gen-agent`
- 用户名: `Xues-idiot`

---

## MoneyPrinterTurbo 参考分析

### 项目概述
- **Stars**: 52k+ ⭐
- **架构**: Python + WebUI + API
- **功能**: 输入主题 → 自动生成视频（文案+素材+字幕+背景音乐）

### 已参考的部分（已实现）
1. ✅ **视频素材搜索** - Pexels/Pixabay API 集成 → `material_collector.py`
2. ✅ **视频生成管道** - moviepy 处理 → `video_generator.py`
3. ✅ **语音合成** - Edge TTS → `voice.py`
4. ✅ **字幕生成** - Whisper → `subtitle.py`

### 可借鉴但尚未充分使用的部分

| 模块 | MoneyPrinterTurbo 做法 | Vox 可借鉴 |
|------|------------------------|-----------|
| **LLM Provider** | 支持 12+ 种 provider（g4f, moonshot, deepseek 等） | 可考虑扩展多 provider 支持 |
| **多 LLM 降级** | 一个 provider 失败自动切换其他 | 可借鉴提高稳定性 |
| **配置文件** | `config.toml` 统一管理 | 可考虑更灵活的 Config 类 |

### MoneyPrinterTurbo 与 Vox 的区别

| 维度 | MoneyPrinterTurbo | Vox |
|------|------------------|-----|
| **核心输出** | 视频文件 | 文案 + 配图建议 |
| **目标平台** | YouTube 等 | 小红书/抖音/公众号/朋友圈 |
| **内容形式** | 通用视频 | 平台适配营销内容 |
| **审核机制** | 无 | 违规词检测 + 质量评分 |

### 辩证思考

**MoneyPrinterTurbo 值得学习**：
- 多 provider 降级机制 → 提高服务稳定性
- 清晰的项目结构（services/ models/ controllers/）
- 素材管理（去重、筛选、缓存）

**MoneyPrinterTurbo 不适合照搬**：
- 视频生成依赖 moviepy（重） vs Vox 只需文案（轻）
- 通用内容 vs 平台定制营销内容
- 无审核机制 vs Vox 必须有违规词检测

---

## 第411轮 自主迭代学习

### 1. 发现的问题

#### 前端 store 版本方法缺失
- `content-store.ts` 中 interface 定义了 `saveVersion` 和 `getVersions`
- 但实际实现缺失，导致类型不完整
- **解决**：补充完整的实现，并添加到 persist 中持久化

#### 内容页面重复 header
- 内容页面同时使用了 SidebarNav 和自己的 header
- SidebarNav 已经包含了 logo 和导航
- **解决**：移除内容页面自己的 header，保持简洁

### 2. 产品思维反思

按照 Vox 核心竞争力思考：

| 组件 | 必要性 | 原因 |
|------|--------|------|
| ProductInput | ✅ 必要 | 产品信息输入是起点 |
| PlatformSelect | ✅ 必要 | 多平台选择是核心功能 |
| CopyOutput | ✅ 必要 | 文案输出展示 |
| ImagePreview | ✅ 必要 | 配图建议是输出的一部分 |
| MarketInsights | ✅ 必要 | 从 store 获取数据，市场调研是核心竞争力 |
| ExportPanel | ✅ 必要 | 导出是核心流程 |
| VideoGenerator | ⚠️ 争议 | 可能是阶段3功能，但作为扩展展示合理 |
| LoadingSpinner | ✅ 必要 | 加载状态必须要有 |

### 3. 市场调研数据流分析

MarketInsights 组件数据来源：
- 从 `useContentStore()` 获取 `marketResearch` 状态
- 在内容生成 API 返回时一起返回，存储在 store 中
- 这是合理的设计，因为市场调研是生成内容时一起做的

### 4. VideoGenerator 定位思考

VideoGenerator 使用文案（script）生成视频，这是：
- 参考 MoneyPrinterTurbo 的功能
- Vox 阶段3功能（短视频脚本：口播文案+分镜）
- 当前阶段1是"多平台文案生成"，视频是延伸功能
- 但在内容页面展示是合理的，因为可以利用生成的文案

### 5. 版本管理思考

- 提交信息应该清晰记录改动内容
- PROGRESS.md 应该按轮次记录
- GitHub push 需要有效的远程仓库配置

### 6. 代码重复发现：PLATFORM_INFO

**发现**：
- `PLATFORM_INFO` 在多个组件中重复定义：
  - `ImagePreview.tsx`: `{ name, icon, color }`
  - `CopyOutput.tsx`: `{ name, icon, color, bgColor }`
- 两者略有不同（CopyOutput 多了 bgColor）
- 可以抽象到一个共享的常量文件中

**决策**：
- 当前不是关键问题，暂不处理
- 如需重构，可创建 `frontend/src/lib/constants.ts`

### 7. 下一步自主迭代方向

1. **前后端联调验证**：检查前端页面是否真正调用后端 API
2. **组件必要性审查**：按产品思维判断每个组件是否需要
3. **用户体验优化**：加载状态、错误处理、toast 提示
4. **GitHub 问题排查**：解决远程仓库 push 失败问题
5. **违规词库完善**：扩展广告法违规词库

---

## 第413轮 违规词库分析

### 当前违规词库统计

| 分类 | 词数 |
|------|------|
| 最高级 | ~24 |
| 绝对化 | ~22 |
| 虚假夸大 | ~16 |
| 疑似违禁 | ~9 |
| 迷信欺诈 | ~14 |
| 医疗虚假 | ~15 |
| 食品违规 | ~10 |
| **总计** | **~110** |

### 问题分析

1. **数量不足**：真实广告法违规词有 1000+ 个，当前只有约 110 个
2. **平台特定规则缺失**：小红书、抖音等平台有各自的社区规则
3. **趋势词缺失**：社交媒体新违规词不断出现

### 改进建议

1. **扩展违规词库**：从广告法源头获取完整词表
2. **添加平台特定规则**：
   - 小红书：医疗、化妆品特定规则
   - 抖音：视频类特定规则
3. **定期更新机制**：参考平台规则变化

### Vox 核心竞争力思考

审核是 Vox 的**杀手锏**之一：
- MoneyPrinterTurbo **无审核**
- Vox 有 **110+ 违规词检测**
- 但还需要**继续完善**

---

## 第412轮 发现并修复 API 调用问题

### 问题：AnalyticsDashboard 使用相对路径

**发现**：
- `AnalyticsDashboard.tsx` 使用 `fetch("/api/v1/analytics/platform")` 相对路径
- 其他所有页面都使用 `${API_BASE_URL}/api/v1/...`
- 相对路径可能导致在生产环境或某些部署场景下 API 调用失败

**解决**：
```tsx
import { API_BASE_URL } from "@/lib/api";
// 改用绝对路径
fetch(`${API_BASE_URL}/api/v1/analytics/platform`)
```

### Sigma Skills 位置记录

用户告知 skills 位置：`D:\PM-AI-Workstation\01-ai-agents\pm-agent-forge\skills`

待研究学习的 Skills：
- `marketing/social-media-marketing/` - 平台选择策略
- `marketing/content-marketing/` - 内容矩阵设计
- `marketing/viral-marketing/` - 传播激励设计
- `common/critical-thinking/` - 逻辑审核
- `common/retry-pattern/` - 重试机制
- `tools/web-search/` - Tavily API

---

## 第415-418轮 迭代优化总结

### 1. 前后端联调问题发现

**问题模式**：
- 多个组件使用相对路径 `fetch('/api/v1/...')`
- 导致在生产环境或某些部署场景下API调用失败

**受影响的组件**：
- ContentCalendar.tsx: 3处
- ContentInspiration.tsx: 2处
- PlatformBestPractices.tsx: 1处

**教训**：
- 建立代码审查机制，检查API调用一致性
- 统一使用 `${API_BASE_URL}/api/v1/...` 绝对路径

### 2. 违规词库扩展

**扩展前**：
- 7个分类
- 约110词

**扩展后**：
- 10个分类（新增：化妆品违规、房地产违规、教育培训违规）
- 350+词

**广告法核心条款**：
- 第九条第（三）项：禁止"最"字系列用语
- 特殊商品/服务有额外限制（化妆品、医疗、食品等）

### 3. 组件生命周期管理

**发现问题**：
- ContentInspiration - 未被任何页面使用
- PlatformBestPractices - 未被任何页面使用

**决策**：
- 保留组件（代表功能规划）
- 但标记为"待集成"

**最佳实践**：
- 未使用的组件不应存在于活跃代码库中
- 可以移到 `_reference/` 或 `_archive/` 目录
- 或者立即删除并记录在TODO中

### 4. 用户体验审计

**审计结果**：
- ErrorBoundary: ✅ 已在layout中使用
- Toast提示: ✅ 各页面已集成
- 加载状态: ✅ 各页面有loading状态
- 错误处理: ✅ 有try-catch和错误提示

**持续改进**：
- 每次新增组件时检查是否有良好的错误处理
- 使用 LoadingSpinner 组件统一加载状态
- 使用 Toast 组件统一提示

### 5. GitHub安全实践

**经验教训**：
- 永远不要在代码库中存储真实secrets
- .gitignore 应包含所有敏感文件
- 文档中的示例应使用占位符
- 提交前使用 grep 检查敏感信息
