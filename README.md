<div align="center">

# Atoms Demo - AI Agent 驱动的代码生成平台

**深度赋智 (DeepSeek/ROOT) 面试项目** · 目标岗位：AI Native 全栈工程师

[![Demo](https://img.shields.io/badge/Demo-在线体验-blue?style=for-the-badge)](https://atoms-demo.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-源码仓库-black?style=for-the-badge&logo=github)](https://github.com/your-username/atoms-demo)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 项目简介

Atoms Demo 是一个受 [Atoms.dev](https://atoms.dev) 启发的 AI Agent 驱动代码生成平台。用户通过自然语言描述需求，由多个专业化 AI Agent 以 SOP 工作流协同完成从需求分析、架构设计到代码实现的全流程，并通过 SSE 实时流式展示 Agent 的思考与执行过程，生成的代码在 iframe 沙箱中即时预览。

核心价值主张：**让想法到可运行应用的距离，从「数天」缩短到「数分钟」**。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 **多 Agent 协作** | 5 个专业化角色（Mike/Emma/Bob/Alex/Iris）以 SOP 流程协同工作 |
| ⚡ **SSE 实时流式** | Agent 思考、执行、代码生成过程全程可视化，体验如同观察真实团队协作 |
| 👁️ **实时预览** | iframe sandbox 渲染生成的 HTML/CSS/JS，支持 PC / Tablet / Mobile 视口切换 |
| 🔄 **4 种执行模式** | Engineer（快速单 Agent） / Team（多 Agent SOP） / Race（多模型竞速） / Research（深度研究） |
| 🔐 **用户认证** | JWT Token + SQLite 持久化，注册/登录/鉴权完整闭环 |
| 📝 **代码版本管理** | 每次生成自动保存版本快照，代码可编辑并实时同步预览 |
| 🎨 **暗色主题专业 UI** | Framer Motion 动画 + Tailwind CSS + 自定义 Design Token，视觉体验对标 Atoms 原版 |

---

## 技术栈

### Frontend

| 技术 | 版本 | 用途 |
|------|------|------|
| Next.js | 16 (App Router) | React 全栈框架，SSR/路由/布局 |
| React | 19 | UI 构建 |
| Tailwind CSS | 4 | 原子化样式 + 自定义 Design Token |
| Zustand | 5 | 轻量级状态管理（Auth/Project/Chat/Preview 四个 Store） |
| Monaco Editor | 4.7 | 代码查看与编辑 |
| Framer Motion | 12 | 页面过渡与微交互动画 |
| Lucide React | 1.25 | 图标库 |
| react-markdown | 10 | Agent 输出 Markdown 渲染 |

### Backend

| 技术 | 版本 | 用途 |
|------|------|------|
| Python FastAPI | 0.104+ | 高性能异步 API 框架 |
| SQLAlchemy | 2.0+ | ORM（支持 SQLite / PostgreSQL） |
| OpenAI SDK | 1.6+ | 兼容 OpenAI API 的 LLM 调用（Agnes AI / DeepSeek / GPT 等） |
| sse-starlette | 1.8+ | SSE 流式响应 |
| python-jose | 3.3+ | JWT Token 生成与验证 |
| passlib | 1.7+ | bcrypt 密码哈希 |
| uvicorn | 0.24+ | ASGI 服务器 |

### 基础设施

| 组件 | 说明 |
|------|------|
| SQLite | 开发环境零配置数据库 |
| PostgreSQL | 生产环境数据库（SQLAlchemy 无缝迁移） |
| Docker Compose | 一键启动前后端 + 数据卷持久化 |
| Vercel | 前端部署 |
| Railway | 后端部署 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend (Next.js)                     │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Chat UI    │  │   Preview    │  │    Code Editor       │  │
│  │   Panel      │  │   Panel      │  │    (Monaco)          │  │
│  │              │  │  (iframe     │  │                      │  │
│  │  · 消息气泡  │  │   sandbox)   │  │  · HTML/CSS/JS       │  │
│  │  · Agent标签 │  │              │  │    语法高亮           │  │
│  │  · 流式输出  │  │  · PC/平板/  │  │  · 实时编辑同步       │  │
│  │  · 模式切换  │  │    手机视口  │  │  · Deploy 按钮       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│  ┌──────┴─────────────────┴──────────────────────┴───────────┐  │
│  │                    Zustand State Store                     │  │
│  │   useAuthStore  ·  useProjectStore  ·  useChatStore       │  │
│  │                      usePreviewStore                       │  │
│  └──────────────────────────┬────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │  HTTP / SSE
┌─────────────────────────────┼───────────────────────────────────┐
│                       Backend (FastAPI)                          │
│                              │                                   │
│  ┌───────────┐  ┌────────────┴──────────┐  ┌────────────────┐  │
│  │  Auth API  │  │   Chat / Agent SSE    │  │  Project API   │  │
│  │            │  │   Stream              │  │                │  │
│  │  · /register│  │  · /message (SSE)    │  │  · CRUD        │  │
│  │  · /login  │  │  · /history           │  │  · 版本管理     │  │
│  │  · /me     │  │                       │  │                │  │
│  └─────┬──────┘  └──────────┬────────────┘  └───────┬────────┘  │
│        │                    │                        │           │
│  ┌─────┴────────────────────┴────────────────────────┴────────┐ │
│  │                   Agent Orchestrator                        │ │
│  │                                                             │ │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐              │ │
│  │  │   Mike    │  │   Emma    │  │    Bob    │              │ │
│  │  │  Leader   │──│    PM     │──│ Architect │              │ │
│  │  │  👨‍💼       │  │  👩‍💻       │  │  🏗️      │              │ │
│  │  └───────────┘  └───────────┘  └───────────┘              │ │
│  │        │                              │                     │ │
│  │        └──────────┬───────────────────┘                     │ │
│  │                   │                                         │ │
│  │         ┌─────────┴──────────┐                              │ │
│  │         │       Alex         │        ┌───────────┐        │ │
│  │         │     Engineer       │        │   Iris    │        │ │
│  │         │       💻           │        │ Researcher│        │ │
│  │         └─────────┬──────────┘        │   🔬      │        │ │
│  │                   │                   └───────────┘        │ │
│  └───────────────────┼─────────────────────────────────────────┘ │
│                      │                                           │
│  ┌───────────────────┴────────────────────────────────────────┐ │
│  │                   LLM Provider Layer                       │ │
│  │   OpenAI-compatible API · Agnes AI · DeepSeek · GPT-4o    │ │
│  │   (无 API Key 时自动降级为 Mock 模式，完整流程可演示)        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ SQLite /     │  │   File       │  │   Project Sandbox    │  │
│  │ PostgreSQL   │  │   Storage    │  │   (代码持久化)        │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 前置要求

- **Node.js** 18+ (推荐 20 LTS)
- **Python** 3.11+
- **pip** 包管理器

### 方式一：本地开发

#### 1. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY 和 OPENAI_BASE_URL（可选，不填则使用 Mock 模式）

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

#### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 配置 API 地址（默认已指向 localhost:8000）
# 如需修改，编辑 .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 启动开发服务器
npm run dev
```

访问 `http://localhost:3000` 即可使用。

### 方式二：Docker Compose 一键启动

```bash
# 克隆仓库
git clone https://github.com/your-username/atoms-demo.git
cd atoms-demo

# 可选：配置 API Key
# 编辑 .env 文件填入 OPENAI_API_KEY（不填则使用 Mock 模式）

# 一键启动
docker-compose up --build
```

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

---

## 项目结构

```
atoms-demo/
├── docker-compose.yml              # Docker 编排（前端 + 后端 + 数据卷）
├── PROJECT_PLAN.md                 # 项目计划书
│
├── backend/                        # Python FastAPI 后端
│   ├── Dockerfile
│   ├── requirements.txt            # Python 依赖
│   ├── .env.example                # 环境变量模板
│   ├── test_api.py                 # API 集成测试
│   ├── test_team.py                # Team 模式测试
│   └── app/
│       ├── main.py                 # FastAPI 入口，路由注册，CORS 配置
│       ├── config.py               # Pydantic Settings，环境变量加载
│       ├── database.py             # SQLAlchemy 异步引擎 + 会话管理
│       ├── agents/                 # 🤖 Agent 系统（核心）
│       │   ├── base.py             # BaseAgent 抽象基类（think/act/execute）
│       │   ├── orchestrator.py     # 编排器：4 种模式路由 + SSE 事件生成
│       │   ├── leader.py           # Mike - Team Leader，任务分解与协调
│       │   ├── pm.py               # Emma - PM，需求分析 + PRD 生成
│       │   ├── architect.py        # Bob - Architect，技术方案设计
│       │   ├── engineer.py         # Alex - Engineer，代码生成 + HTML 提取
│       │   └── researcher.py       # Iris - Researcher，深度研究
│       ├── models/                 # SQLAlchemy ORM 模型
│       │   ├── user.py             # 用户模型
│       │   ├── project.py          # 项目模型
│       │   ├── conversation.py     # 对话模型
│       │   ├── message.py          # 消息模型
│       │   ├── code_version.py     # 代码版本模型
│       │   └── agent_log.py        # Agent 执行日志模型
│       ├── schemas/                # Pydantic 请求/响应 Schema
│       │   ├── user.py
│       │   ├── project.py
│       │   ├── chat.py
│       │   └── agent.py
│       ├── routers/                # API 路由
│       │   ├── auth.py             # 认证（注册/登录/当前用户）
│       │   ├── projects.py         # 项目 CRUD + 版本管理
│       │   ├── chat.py             # 对话消息 + SSE 流式端点
│       │   └── preview.py          # 代码预览（HTML 渲染）
│       ├── services/               # 业务逻辑层
│       │   ├── auth_service.py     # JWT 生成/验证 + 密码哈希
│       │   ├── chat_service.py     # 对话管理 + Agent 调度
│       │   └── project_service.py  # 项目 + 版本管理
│       └── utils/
│           └── llm.py              # LLM Provider（OpenAI API + Mock 降级）
│
└── frontend/                       # Next.js 前端
    ├── Dockerfile
    ├── package.json
    ├── next.config.ts
    ├── tailwind.config.ts
    ├── postcss.config.mjs
    ├── tsconfig.json
    ├── public/                     # 静态资源
    └── src/
        ├── app/                    # Next.js App Router 页面
        │   ├── page.tsx            # 首页（Hero + Agent 介绍 + Features）
        │   ├── layout.tsx          # 根布局
        │   ├── globals.css         # 全局样式 + Design Token
        │   ├── login/             # 登录/注册页
        │   │   └── page.tsx
        │   ├── dashboard/         # 项目仪表盘
        │   │   └── page.tsx
        │   └── workspace/         # 工作区（核心交互页）
        │       └── [projectId]/
        │           └── page.tsx
        ├── components/             # React 组件
        │   ├── chat/              # 对话相关
        │   │   ├── ChatPanel.tsx   # 对话面板（消息列表 + 输入框）
        │   │   ├── ChatInput.tsx   # 输入框 + 模式切换
        │   │   └── MessageBubble.tsx  # 消息气泡（用户/Agent/系统）
        │   ├── preview/           # 预览相关
        │   │   ├── PreviewPanel.tsx   # iframe 预览面板
        │   │   └── ViewportToggle.tsx # PC/Tablet/Mobile 视口切换
        │   ├── editor/            # 编辑器相关
        │   │   ├── CodeEditor.tsx     # Monaco Editor 代码查看
        │   │   └── WorkflowPanel.tsx   # Agent 工作流可视化
        │   ├── dashboard/         # 仪表盘相关
        │   │   ├── ProjectCard.tsx     # 项目卡片
        │   │   └── TemplateCard.tsx    # 模板卡片
        │   └── ui/                # 基础 UI 组件
        │       ├── Button.tsx
        │       ├── Card.tsx
        │       ├── Input.tsx
        │       ├── Badge.tsx
        │       └── Skeleton.tsx
        └── lib/                   # 工具库
            ├── api.ts             # API 客户端（fetch 封装 + SSE 流解析）
            ├── store.ts           # Zustand Store（Auth/Project/Chat/Preview）
            ├── types.ts           # TypeScript 类型定义
            ├── agents.ts          # Agent 元数据（名称/角色/Emoji）
            └── utils.ts           # 工具函数
```

---

## 核心流程说明

### Engineer Mode — 快速单 Agent 生成

```
用户输入 "做一个计算器应用"
        │
        ▼
   Alex (Engineer) ─── 思考：分析需求 ─── 执行：直接生成代码
        │
        ▼
   代码生成 → iframe 实时预览
```

**适用场景**：简单应用、快速原型、需求明确时直接出代码。

### Team Mode — 多 Agent SOP 协作

```
用户输入 "做一个数据分析 Dashboard"
        │
        ▼
   Mike (Leader) ─── 思考：任务分解 ─── 执行：制定执行计划
        │  "Emma 分析需求 → Bob 设计架构 → Alex 实现"
        ▼
   Emma (PM) ─── 思考：需求分析 ─── 执行：输出 PRD（功能列表/用户故事/验收标准）
        │
        ▼
   Bob (Architect) ─── 思考：技术选型 ─── 执行：输出架构文档（技术栈/组件结构/设计系统）
        │
        ▼
   Alex (Engineer) ─── 思考：实现规划 ─── 执行：基于 PRD + 架构生成完整代码
        │
        ▼
   代码生成 → iframe 实时预览
```

**适用场景**：复杂应用、需要需求分析和架构设计的项目。每个 Agent 的输出作为下一个 Agent 的输入（`enriched_context`），形成完整的 SOP 流水线。

### Race Mode — 同模型不同策略并行

```
用户输入 "做一个 Landing Page"
        │
        ├──▶ Variant A（原始 Prompt） ──▶ Alex 生成版本 A
        │
        └──▶ Variant B（创意 Prompt） ──▶ Alex 生成版本 B
        │
        ▼
   版本 A vs 版本 B 并排对比 → 用户选择最优
```

**适用场景**：创意类项目、需要多方案比较时。通过 `asyncio.gather` 并行调用同一模型但不同 Prompt 策略，总耗时 ≈ 单次生成耗时。未来可扩展为跨模型对比。

### Research Mode — 深度研究

```
用户输入 "分析 2024 年前端框架趋势"
        │
        ▼
   Iris (Researcher) ─── 思考：分析主题 ─── 执行：输出研究报告
        │  （研究发现 / 最佳实践 / 推荐建议）
        ▼
   Markdown 渲染展示
```

**适用场景**：技术调研、方案评估、知识整理。不生成代码，输出结构化研究报告。

---

## 实现思路与关键取舍

### 为什么选 FastAPI 而不是 Go / Node.js？

| 维度 | FastAPI (Python) | Go | Node.js |
|------|-------------------|-----|---------|
| LLM 生态 | OpenAI/LangChain 原生 Python SDK | 需自行封装 | SDK 存在但生态弱于 Python |
| 开发速度 | 类型提示 + 自动 API 文档，极快 | 编译型语言，迭代慢 | 中等 |
| 异步支持 | async/await + uvicorn，性能足够 | goroutine 最强 | 事件循环，好 |
| Agent 编排 | 动态 prompt 构建极灵活 | 静态语言，prompt 构建繁琐 | 中等 |

**结论**：对于 AI Agent 驱动项目，Python 的 LLM 生态和灵活的字符串处理能力是决定性优势。FastAPI 的性能（uvicorn + asyncio）对本 Demo 完全足够。

### 为什么选 OpenAI-compatible API？

采用 `OPENAI_BASE_URL + OPENAI_API_KEY + LLM_MODEL` 三参数配置，兼容所有 OpenAI API 格式的提供商：

- **Agnes AI** (`agnes-2.0-flash`) — 默认模型
- **DeepSeek** (`deepseek-chat`) — 国产高性价比
- **OpenAI GPT-4o** — 能力最强
- **本地模型** (Ollama/vLLM) — 隐私敏感场景

只需修改 `.env` 中的三个参数即可切换模型，零代码改动。

### 为什么选 SSE 而不是 WebSocket？

- Agent 执行是**单向推送**（服务端 → 客户端），SSE 天然适配
- SSE 基于 HTTP，无需额外协议握手，**实现更简单**
- SSE 自动重连，**运维成本低**
- 浏览器原生 `EventSource` / `fetch` API 支持，**前端集成零依赖**

WebSocket 的优势在于双向通信，但本项目不需要客户端向服务端主动推送（用户消息通过普通 POST 发送）。

### 为什么选 SQLite 而不是 PostgreSQL？

| 维度 | SQLite | PostgreSQL |
|------|--------|------------|
| 零配置 | ✅ 无需安装数据库 | ❌ 需要独立部署 |
| Demo 友好 | ✅ 文件即数据库，开箱即用 | ❌ 需要连接字符串配置 |
| 迁移成本 | SQLAlchemy ORM 抽象，切换只需改一行 `DATABASE_URL` | — |
| 生产部署 | ❌ 并发写入瓶颈 | ✅ 成熟方案 |

**结论**：Demo 阶段零配置体验优先，生产环境只需修改 `DATABASE_URL` 即可平滑迁移到 PostgreSQL。

### Mock 模式设计

当 `OPENAI_API_KEY` 为空或以 `your-` 开头时，`LLMProvider` 自动降级为 Mock 模式：

- **Leader** → 返回预设的执行计划 JSON
- **PM** → 返回预设的 PRD JSON
- **Architect** → 返回预设的架构文档 JSON
- **Engineer** → 根据 Prompt 关键词匹配（dashboard/portfolio/landing/calculator）返回对应的完整 HTML
- **Researcher** → 返回预设的研究报告 JSON

Mock 模式下**整个流程可完整演示**，包括 SSE 事件推送、Agent 状态流转、代码预览，只是生成内容为预设模板而非 LLM 实时生成。

---

## 当前完成程度

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户注册/登录/JWT 认证 | ✅ | 完整闭环，bcrypt 密码哈希 + 7天有效期 Token |
| 项目 CRUD 和版本管理 | ✅ | 创建/列表/详情/删除 + 代码版本快照 |
| Engineer Mode | ✅ | 单 Agent 快速生成，SSE 流式输出 |
| Team Mode | ✅ | Mike→Emma→Bob→Alex 四 Agent SOP 协作 |
| Race Mode | ✅ | 同模型不同 Prompt 策略并行生成双变体，A/B 版本对比 |
| Research Mode | ✅ | Iris 深度研究 + Markdown 渲染 |
| SSE 实时流式输出 | ✅ | agent_thinking / agent_action / code_generated / message_complete 四类事件 |
| iframe 实时代码预览 | ✅ | PC / Tablet / Mobile 视口切换 |
| Monaco Editor 代码查看 | ✅ | 语法高亮，可编辑并实时同步预览 |
| Agent 工作流可视化 | ✅ | 实时展示当前活跃 Agent 和执行进度 |
| 项目设置/部署/删除 | ✅ | 编辑项目名称/描述/模式 + Deploy 按钮 + 删除项目 |
| 暗色主题 UI | ✅ | 自定义 Design Token + Framer Motion 动画 |
| Mock 模式 | ✅ | 无 API Key 完整流程可演示 |
| Docker Compose 一键部署 | ✅ | 前后端 + 数据卷，`docker-compose up` 即用 |
| OpenAI API 文档 | ✅ | FastAPI 自动生成 Swagger UI |

---

## 如果继续投入时间

### P0 — 核心竞争力提升

- **接入更多 LLM 提供商**：DeepSeek V3、GPT-4o、Claude 3.5 Sonnet，支持 Race Mode 跨模型对比（目前 Race Mode 用同一模型不同 Prompt）
- **可视化拖拽编辑器**：类似 Atoms 的 Visual Editor，点击预览中的元素即可定位到对应代码行并编辑，修改后热更新预览
- **更丰富的 Mock 模板**：E-commerce、Blog、CRM 等更多场景模板，让无 API Key 的演示体验更丰富

### P1 — 产品完整度

- **Supabase 后端集成**：用户认证、实时数据库、AI Wallet 计费，替代自建 Auth + SQLite
- **代码导出和 GitHub 同步**：生成的代码一键推送到 GitHub 仓库，支持持续迭代
- **对话历史持久化与回放**：完整保存每次对话的 Agent 执行日志，支持回放和分享
- **代码 Diff 可视化**：迭代修改时展示代码变更差异

### P2 — 生态扩展

- **移动端适配优化**：响应式布局已在，但交互体验（触控、虚拟键盘）需专门优化
- **App World 分享社区**：用户可将生成的应用发布到社区，供他人浏览、Fork 和二次创作
- **模板市场**：预置高质量模板，用户可从模板快速衍生新项目
- **多语言支持 (i18n)**：中英文界面切换

---

## License

[MIT](LICENSE)
