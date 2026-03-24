# Vox - 内容生成 Agent

> 代号 Vox (声)，意为"声音、音频内容生成"

**Vox** 是一个垂直领域的内容生成 Agent，专注于**文案+配图**的组合输出，服务于小红书、抖音、公众号、朋友圈等多平台营销内容生成。

## 核心功能

- **多平台文案生成**：小红书、抖音、公众号、朋友圈
- **智能内容规划**：基于产品特点自动分析目标用户
- **AI 配图建议**：生成适合各平台的配图提示词
- **违规词检测**：自动检测并提示广告法违规词（含分类和替换建议）
- **文案质量评估**：结构分析、评分、改进建议
- **多格式导出**：JSON、Markdown、HTML、纯文本

## 配色方案

- **主色**: #FF6B35 (活力橙)
- **辅色**: #FF8C61 (珊瑚橙)
- **点缀**: #FFD93D (明黄)
- **背景**: #FFF8F0 (暖白)

## 快速开始

### 1. 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端
cd frontend && npm install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API Key：

```bash
MINIMAX_API_KEY=your_api_key
MINIMAX_BASE_URL=https://api.minimaxi.com/anthropic
MINIMAX_MODEL=MiniMax-M2.2
```

### 3. 启动服务

```bash
# 后端 API (端口 8003)
python main.py

# 前端 (端口 3666) - 新终端
cd frontend
npm run dev
```

### 4. 访问

- 前端页面: http://localhost:3666
- API 文档: http://localhost:8003/docs

## 项目结构

```
content-gen-agent/
├── backend/
│   ├── agents/
│   │   ├── planner.py       # 内容规划 Agent
│   │   ├── copywriter.py    # 多平台文案生成
│   │   ├── reviewer.py      # 违规词检测 + 质量评分
│   │   └── exporter.py      # 多格式导出
│   ├── api/
│   │   └── content.py       # FastAPI 接口
│   ├── prompts/             # Prompt 模板
│   │   ├── xiaohongshu.py   # 小红书
│   │   ├── tiktok.py        # 抖音
│   │   ├── official.py       # 公众号
│   │   └── friend.py         # 朋友圈
│   ├── services/
│   │   └── llm.py           # LLM 客户端 (重试机制)
│   ├── tools/
│   │   └── image_gen.py     # 图像生成
│   └── graph/
│       └── content_graph.py # 工作流编排
├── frontend/
│   └── src/
│       ├── app/             # Next.js 15 页面
│       ├── components/      # React 19 组件 (Motion 动画)
│       ├── store/           # Zustand 状态管理
│       └── lib/             # 工具函数
├── tests/                   # pytest 测试用例
│   ├── conftest.py         # fixtures
│   ├── test_planner.py
│   ├── test_copywriter.py
│   ├── test_reviewer.py
│   ├── test_exporter.py
│   ├── test_api.py
│   ├── test_llm.py
│   └── test_integration.py
├── main.py                  # 后端入口
├── config.toml              # 配置文件
└── requirements.txt         # Python 依赖
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python, FastAPI, Pydantic, LangGraph |
| 前端 | Next.js 15, React 19, TypeScript |
| 样式 | Tailwind CSS v4, Motion |
| 状态 | Zustand |
| AI | MiniMax API (兼容 Anthropic) |

## API 接口

### 生成内容

```bash
POST /api/v1/content/generate

{
  "product": {
    "name": "智能睡眠枕",
    "description": "AI智能枕头",
    "selling_points": ["改善睡眠", "AI监测"],
    "target_users": ["加班族", "失眠人群"],
    "category": "家居"
  },
  "platforms": ["xiaohongshu", "tiktok"]
}
```

### 审核文案

```bash
POST /api/v1/content/review
Content: "这是最好的产品..."
```

### 获取平台列表

```bash
GET /api/v1/platforms
```

### 健康检查

```bash
GET /health
```

## 开发

```bash
# 运行后端测试
python -m pytest tests/ -v

# 运行前端开发服务器
cd frontend && npm run dev
```

## 已用 Sigma Skills

- `marketing/social-media-marketing/` - 平台选择策略
- `marketing/content-marketing/` - 内容矩阵设计
- `common/critical-thinking/` - 逻辑审核
- `common/retry-pattern/` - 重试机制

## License

MIT
