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
