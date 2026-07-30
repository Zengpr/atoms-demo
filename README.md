<div align="center">

# Atoms Demo - AI Agent 驱动的代码生成平台

**深度赋智 (ROOT) 面试项目** · 目标岗位：AI Native 全栈工程师

[![Demo](https://img.shields.io/badge/Demo-在线体验-blue?style=for-the-badge)](https://frontend-production-e558.up.railway.app)
[![Backend](https://img.shields.io/badge/API-Railway-green?style=for-the-badge)](https://backend-api-production-8923.up.railway.app/docs)
[![GitHub](https://img.shields.io/badge/GitHub-源码仓库-black?style=for-the-badge&logo=github)](https://github.com/Zengpr/atoms-demo)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 项目简介

Atoms Demo 是一个受 [Atoms.dev](https://atoms.dev) 启发的 AI Agent 驱动代码生成平台。用户通过自然语言描述需求，由多个专业化 AI Agent 以 SOP 工作流协同完成从需求分析、架构设计到代码实现的全流程，并通过 SSE 实时流式展示 Agent 的思考与执行过程，生成的代码在 iframe 沙箱中即时预览。

核心价值主张：**让想法到可运行应用的距离，从「数天」缩短到「数分钟」**。

---

## 🚀 快速体验

| 方式 | 说明 |
|------|------|
| **游客模式** | 首页点击 "Try as Guest" 按钮，一键创建临时账号，无需注册 |
| **测试账号** | 邮箱: `demo@atoms-demo.app`，密码: `demo2024`（预置项目，直接可用） |

> ⚠️ 使用真实 LLM (DeepSeek V4 Pro)，非 Mock。生成代码使用 Tailwind CSS + Inter 字体。国内直连可用。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 **多 Agent 协作** | 8 个专业化角色（Mike/Emma/Bob/Alex/Iris/Sarah/Adrian/David）以 SOP 流程协同工作 |
| ⚡ **SSE 实时流式** | Agent 思考（含设计文档）、执行、代码生成过程全程可视化，体验如同观察真实团队协作 |
| 👁️ **实时预览** | iframe sandbox 渲染生成的 HTML/CSS/JS，支持 PC / Tablet / Mobile 视口切换 |
| 🔄 **5 种执行模式** | Engineer（快速单 Agent） / Team（多 Agent SOP） / Race（多模型竞速） / Research（深度研究） / Review（审查修复） |
| 🔐 **用户认证** | JWT Token + SQLite 持久化，注册/登录/鉴权完整闭环，游客一键体验 |
| 📝 **代码版本管理** | 每次生成自动保存版本快照，代码可编辑并实时同步预览 |
| 🛡️ **截断修复** | 自动检测 JS 截断（括号不平衡/未闭合 script），最多 3 次自动续写 |
| 🧠 **Think Step** | Engineer 代码生成前先输出设计文档（功能规划/技术方案/UI设计），流式展示完整实现过程 |
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
| OpenAI SDK | 1.6+ | 兼容 OpenAI API 的 LLM 调用（DeepSeek V4 Pro / GPT 等） |
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
| Vercel | 前端部署（国内 DNS 污染，改用 Railway） |
| Railway | 前端 + 后端部署 |

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
│  │   OpenAI-compatible API · DeepSeek V4 Pro · GPT-4o        │ │
│  │   自动截断续写(3次) + Think Step设计文档 + 600s超时保护    │ │
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
# 编辑 .env，填入 OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL
# 推荐 DeepSeek V4 Pro（国内可用）:
#   OPENAI_API_KEY=sk-xxx
#   OPENAI_BASE_URL=https://api.deepseek.com
#   LLM_MODEL=deepseek-v4-pro

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
git clone https://github.com/Zengpr/atoms-demo.git
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

### Engineer Mode — 快速单 Agent 生成（含 Think Step）

```
用户输入 "做一个计算器应用"
        │
        ▼
   Alex (Engineer)
   ├── Think Step: 分析需求→输出设计文档（功能规划/技术方案/UI设计/关卡设计）
   │   (流式展示为 agent_stream + agent_thinking 事件)
   └── Act Step: 1句中文总结 + 完整代码
        │
        ▼
   代码生成 → iframe 实时预览
```

**适用场景**：简单应用、快速原型、需求明确时直接出代码。默认模式。

**Think Step 机制**：代码生成前先让 LLM 输出结构化设计文档（max_tokens=2048），流式显示给用户，让生成过程透明可理解。设计文档与代码分离，避免设计文本被 `extract_html()` 误提取导致 iframe 空白。

### Team Mode — 多 Agent SOP 协作

```
用户输入 "做一个数据分析 Dashboard"
        │
        ▼
   Mike (Leader) ─── 思考：任务分解 ─── 执行：制定执行计划
        │  "Emma 分析需求 → Bob 设计架构 → Alex 实现"
        │  (简单迭代时 Mike 直接指派 Alex，跳过 PM/Architect)
        ▼
   Emma (PM) ─── 思考：需求分析 ─── 执行：输出 PRD（功能列表/用户故事/验收标准）
        │
        ▼
   Bob (Architect) ─── 思考：技术选型 ─── 执行：输出架构文档（技术栈/组件结构/设计系统）
        │
        ▼
   Alex (Engineer)
   ├── Think Step: 输出设计文档
   └── Act Step: 基于 PRD + 架构生成完整代码
        │
        ▼
   代码生成 → iframe 实时预览
```

**适用场景**：复杂应用、需要需求分析和架构设计的项目。每个 Agent 的输出作为下一个 Agent 的输入（`enriched_context`），形成完整的 SOP 流水线。Leader 对简单修改默认只派 Engineer，不走全 pipeline。

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

### Review Mode — 审查修复

```
用户输入 "修复这个项目的 Bug"
        │
        ▼
   Iris (Reviewer) ─── 审查代码 ─── 输出问题列表 + 修复建议
        │
        ▼
   Alex (Engineer) ─── 基于审查结果修复代码
        │
        ▼
   代码更新 → iframe 实时预览
```

**适用场景**：代码审查、Bug 修复、质量改进。

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

- **DeepSeek V4 Pro** (`deepseek-v4-pro`) — 当前生产模型，国内可用，65K token 输出
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
| 游客一键体验 | ✅ | 首页 "Try as Guest" 按钮，无需注册 |
| 项目 CRUD 和版本管理 | ✅ | 创建/列表/详情/删除 + 代码版本快照 |
| Engineer Mode (含 Think Step) | ✅ | 设计文档流式输出 → 代码生成，默认模式 |
| Team Mode | ✅ | Mike→Emma→Bob→Alex 四 Agent SOP 协作，简单迭代智能跳步 |
| Race Mode | ✅ | 同模型不同 Prompt 策略并行生成双变体，A/B 版本对比 |
| Research Mode | ✅ | Iris 深度研究 + Markdown 渲染 |
| Review Mode | ✅ | Iris审查代码→Alex修复改进 |
| SSE 实时流式输出 | ✅ | agent_thinking / agent_stream / agent_action / code_generated / message_complete 五类事件 |
| Think Step 设计文档 | ✅ | Engineer 代码生成前输出功能规划/技术方案/UI设计，max_tokens=2048 |
| 截断检测+自动续写 | ✅ | 检测最后一个 script 块未闭合，最多 3 次自动续写 |
| LLM 超时保护 | ✅ | 总超时 600s + httpx Timeout(30/600/30/30) |
| iframe 实时代码预览 | ✅ | PC / Tablet / Mobile 视口切换，0 sandbox 错误 |
| Monaco Editor 代码编辑 | ✅ | 语法高亮，可编辑并实时同步预览 |
| 迭代修改 | ✅ | 基于对话历史 + 上次代码上下文，Agent 在已有代码上增量修改 |
| Console 错误自动修复 | ✅ | iframe 错误捕获→自动反馈给 AI 修复 |
| 代码恢复 | ✅ | 页面刷新后从 /latest-code 端点恢复预览 |
| Agent 工作流可视化 | ✅ | 实时展示当前活跃 Agent 和执行进度 |
| 模板/Remix系统 | ✅ | 8个预置模板 + 后端Templates API |
| 版本历史UI + 一键回滚 | ✅ | Versions标签页 + Restore API |
| 真实Deploy | ✅ | 生成公开URL，无需登录即可访问 |
| 文件树 | ✅ | FileTree组件，解析HTML→CSS/JS/HTML结构 |
| 上传文件/附件 | ✅ | 📎附件按钮+后端file_contexts传递给Agent |
| 下载项目文件 | ✅ | 一键下载HTML，Preview工具栏 |
| Issue Report | ✅ | 🐛一键修Bug按钮，自动生成修复请求 |
| 暗色主题 UI | ✅ | 自定义 Design Token + Framer Motion 动画 |
| 全站中文 UI | ✅ | 所有文案和 Agent 回复均中文 |
| Mock 模式 | ✅ | 无 API Key 完整流程可演示 |
| Docker Compose 一键部署 | ✅ | 前后端 + 数据卷，`docker-compose up` 即用 |
| OpenAI API 文档 | ✅ | FastAPI 自动生成 Swagger UI |
| Railway 线上部署 | ✅ | 前端+后端均 Online，E2E 全验证通过 |
| 大型项目 E2E 验证 | ✅ | Mario 57K/Dashboard 31K/Ecommerce 33K/Snake 35K/KOF 61K 全通过 |

---

## 如果继续投入时间

### P0 — 核心竞争力提升

- **SEARCH/REPLACE diff 迭代**：Aider 风格差量编辑，避免每次完整重写，节省 token、加速迭代
- **PostgreSQL 迁移**：SQLAlchemy 抽象已就绪，换连接字符串即可，解决 SQLite 并发瓶颈
- **跨模型 Race**：接入 Claude/GPT/DeepSeek 多模型对比（目前 Race 用同一模型不同 Prompt）

### P1 — 产品完整度

- **视觉自验证循环**：Headless 浏览器截图→LLM 对比→自动修复，代码质量闭环
- **Visual Editor**：点击预览元素→侧边栏编辑属性，对标 Atoms 拖拽式编辑器
- **@-mention 指定 Agent**：用户可通过 @Alex 直接指定 Agent
- **代码 Diff 可视化**：迭代修改时展示代码变更差异

### P2 — 生态扩展

- **移动端适配优化**：响应式布局已在，但交互体验（触控、虚拟键盘）需专门优化
- **App World 分享社区**：用户可将生成的应用发布到社区，供他人浏览、Fork 和二次创作
- **模板市场**：预置高质量模板，用户可从模板快速衍生新项目
- **多语言支持 (i18n)**：中英文界面切换

---

## 设计思路与实现方案

### 一、问题定义

**目标**：构建一个 AI Agent 驱动的代码生成平台，让非技术用户通过自然语言描述即可获得可运行的应用代码。

**核心挑战**：

1. **单次生成质量不足** — 简单的「Prompt → Code」模式无法处理复杂需求
2. **过程不可观测** — 用户等待 30 秒看到结果，中间无任何反馈，体验极差
3. **无法迭代改进** — 生成后无法基于已有代码增量修改，每次从头开始
4. **代码不可执行** — 生成的是代码片段而非完整可运行应用

### 二、系统设计哲学

#### 2.1 SOP 工作流优于单次生成

借鉴真实软件团队的工作方式，将「一个人写代码」升级为「PM 分析需求 → Architect 设计方案 → Engineer 编码实现」的 SOP 流水线：

```
单个 Agent 生成:  用户 ──▶ LLM ──▶ 代码
                    ↑ 一次调用，质量取决于 prompt

SOP 工作流:       用户 ──▶ Mike(分解) ──▶ Emma(PRD) ──▶ Bob(架构) ──▶ Alex(编码) ──▶ 代码
                    ↑ 多步编排，每步聚焦，上下文递进丰富
```

**关键洞察**：每个 Agent 的输出（PRD/架构文档）作为下一个 Agent 的输入（enriched_context），使得 Engineer Agent 拥有远超单次调用的上下文信息，代码质量显著提升。

#### 2.2 可观测性优先

用户不信任黑盒。SSE 流式推送每个 Agent 的**思考过程**（agent_stream）和**执行结果**（agent_action），让用户感受到「真实的团队在为我工作」：

```
时间轴:
0s    ──▶ Mike: "我将协调团队完成这个项目..."     (agent_stream, 打字机效果)
1.5s  ──▶ Mike: "执行计划：Emma→Bob→Alex"          (agent_action)
2s    ──▶ Emma: "正在分析需求..."                   (agent_stream)
4s    ──▶ Emma: "PRD: 响应式布局、暗色主题..."       (agent_action)
5s    ──▶ Bob: "技术栈：HTML5+CSS3+JS..."           (agent_stream)
7s    ──▶ Bob: "架构：Header→Hero→Features..."      (agent_action)
8s    ──▶ Alex: "正在编写代码..."                    (agent_stream)
15s   ──▶ Alex: [完整HTML代码]                       (code_generated)
16s   ──▶ Mike: "团队协作完成！预览已生成"            (message_complete)
```

#### 2.3 迭代修改上下文

第二次及后续对话时，系统自动注入：

- **对话历史**（最近 10 条消息摘要）
- **上次生成代码**（完整 HTML）
- **迭代标记** (`is_iteration=True`)

Engineer Agent 基于已有代码进行增量修改，而非从零生成。Mock 模式实现了 4 种迭代策略：

| 迭代请求 | Mock 策略 |
|----------|-----------|
| dark mode / 暗色 | 在原有代码中添加 dark mode CSS 变量 + toggle 按钮 |
| 换色 / color | 替换主色调 CSS 变量 |
| 动画 / animation | 添加 CSS keyframes 动画类 |
| 其他 | 添加响应式表单组件 |

### 三、架构设计

#### 3.1 分层架构

```
┌─────────────────────────────────┐
│        Presentation Layer        │  Next.js (React) + Zustand
│   Pages / Components / Stores   │  SSR + CSR 混合渲染
├─────────────────────────────────┤
│         API Gateway Layer        │  FastAPI Routers
│   Auth / Projects / Chat / SSE  │  JWT 鉴权 + 请求验证
├─────────────────────────────────┤
│        Business Logic Layer      │  Services + Orchestrator
│   对话管理 / Agent 调度 / 上下文  │  SSE 事件编排
├─────────────────────────────────┤
│          Agent Layer             │  5 个专业化 Agent
│   Leader / PM / Architect /     │  BaseAgent 抽象基类
│   Engineer / Researcher         │  think() → act() → execute()
├─────────────────────────────────┤
│        Data Access Layer         │  SQLAlchemy ORM
│   User / Project / Message /    │  异步 Engine + Session
│   CodeVersion / AgentLog        │  SQLite / PostgreSQL
├─────────────────────────────────┤
│        LLM Provider Layer        │  OpenAI-compatible SDK
│   Agnes AI / DeepSeek / GPT-4o  │  Mock 降级保障
└─────────────────────────────────┘
```

#### 3.2 SSE 事件协议

定义 5 种标准 SSE 事件类型，覆盖 Agent 执行全生命周期：

| 事件 | 方向 | 数据格式 | 说明 |
|------|------|----------|------|
| `agent_thinking` | Server → Client | `{agent, emoji, message}` | Agent 开始思考，显示 spinner（同一 agent 去重，不重复创建） |
| `agent_stream` | Server → Client | `{agent, emoji, chunk}` | 思考过程/设计文档文本片段（打字机效果，最多显示 2000 字符） |
| `agent_action` | Server → Client | `{agent, emoji, action, duration_ms, ...}` | Agent 完成一步操作（含 PRD/架构/代码富内容展示） |
| `code_generated` | Server → Client | `{agent, code, duration_ms}` | 完整代码生成，自动刷新 Preview |
| `message_complete` | Server → Client | `{agent, message, duration_ms, agents_used}` | 整轮对话结束（动态完成消息，包含 LLM 实际输出内容） |

前端通过 `async generator` 消费 SSE 流：

```typescript
async function* streamChat(projectId, content, mode): AsyncGenerator<SSEMessage> {
  const res = await fetch(SSE_BASE + '/api/chat/' + projectId + '/message', { ... });
  const reader = res.body.getReader();
  // 逐行解析 SSE 格式: "event: xxx\ndata: {...}\n\n"
  // yield { event, data } 给调用方
}
```

#### 3.3 Orchestrator 编排模式

```python
class Orchestrator:
    async def run(self, user_message, mode, context) -> AsyncIterator[dict]:
        if mode == "engineer":
            # Think Step(设计文档) + 单 Agent 快速路径
            async for event in self._run_engineer(user_message, context):
                yield event

        elif mode == "team":
            # SOP 流水线：Mike → Emma → Bob → Alex（简单迭代跳步）
            async for event in self._run_team(user_message, context):
                yield event

        elif mode == "race":
            # 并行竞速：两个变体同时生成
            async for event in self._run_race(user_message, context):
                yield event

        elif mode == "research":
            # 深度研究：Iris 独立执行
            async for event in self._run_research(user_message, context):
                yield event

        elif mode == "review":
            # 审查修复：Iris 审查 → Alex 修复
            async for event in self._run_review(user_message, context):
                yield event
```

每种模式的 SSE 事件序列：

- **Engineer**: `agent_thinking → agent_stream*(设计文档) → agent_thinking → agent_stream*(代码) → agent_action → code_generated → message_complete`
- **Team**: 4 组 `agent_thinking → agent_stream* → agent_action` → `code_generated → message_complete`（Leader 智能跳步）
- **Race**: 2 组并行 `agent_thinking → agent_stream* → agent_action` → 2 个 `code_generated` → `message_complete`
- **Research**: `agent_thinking → agent_stream* → agent_action → message_complete`
- **Review**: 2 组 `agent_thinking → agent_stream* → agent_action` → `code_generated → message_complete`

**关键保护机制**：
- **截断续写**：`is_js_truncated()` 检测最后一个 `<script>` 块未闭合或 HTML 结尾缺少 `</script></body></html>`，自动调用 `_continue_code()` 续写，最多 3 次
- **超时保护**：`LLM_TOTAL_TIMEOUT=600s` 总超时 + httpx `connect=30s, read=600s`
- **Heartbeat 限制**：`MAX_HEARTBEATS=2`，防止无限心跳占用连接
- **JSON 解析容错**：`_try_parse_json()` 支持 markdown fence 提取 + brace fallback

#### 3.4 前端状态管理

4 个独立 Zustand Store，职责清晰：

| Store | 状态 | 关键方法 |
|-------|------|----------|
| `useAuthStore` | user, token, isAuthenticated | login, register, logout, loadUser |
| `useProjectStore` | projects, currentProject | loadProjects, createProject, selectProject |
| `useChatStore` | messages, isStreaming, currentMode | addMessage, updateLastAgentMessage, loadHistory |
| `usePreviewStore` | previewHtml | setPreviewHtml |

**关键设计**：`updateLastAgentMessage(msgId, chunk)` 支持流式文本追加更新，实现打字机效果。每收到 `agent_stream` 事件，前端将 chunk 追加到对应消息的 `metadata.streamText` 字段。

#### 3.5 数据模型与 camelCase 转换

后端 Python 使用 `snake_case`，前端 TypeScript 使用 `camelCase`。通过 Pydantic 的 `alias_generator=to_camel` + `model_config = ConfigDict(populate_by_name=True)` 统一处理：

```python
class CAMEL_CONFIG:
    alias_generator = staticmethod(to_camel)
    populate_by_name = True

class ProjectResponse(BaseModel):
    user_id: str          # 序列化为 userId
    created_at: datetime  # 序列化为 createdAt
    model_config = CAMEL_CONFIG
```

### 四、关键实现细节

#### 4.1 SSE 流中的 DB Session 管理

**问题**：FastAPI 的 `Depends(get_db)` 会在请求结束时关闭 Session，但 SSE 流是长时间运行的，如果共享同一个 Session，流内数据库操作会因 Session 关闭而失败。

**解决**：SSE 流内使用独立的 `async_session()`：

```python
async def event_stream():
    async with async_session() as stream_db:  # 独立 session
        async for event in process_chat(stream_db, project_id, mode, content):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
        await stream_db.commit()
```

#### 4.2 SQLAlchemy `metadata` 字段冲突

**问题**：`Message` 模型的 `metadata_` 字段映射到数据库列 `metadata`，但 SQLAlchemy 的 `Base.metadata` 是保留属性（`MetaData` 对象）。`model_validate(m)` 时 Pydantic 读到 `m.metadata` 得到 `MetaData` 而非 JSON 字段。

**解决**：History 端点手动构造 dict：

```python
result.append({
    "id": m.id,
    "conversationId": m.conversation_id,
    "metadata": m.metadata_,  # 读取 Python 属性而非 DB 列名
    "createdAt": m.created_at.isoformat(),
})
```

#### 4.3 SSE 绕过 Next.js 代理

**问题**：Next.js 的 `rewrites` 代理会缓冲 SSE 流，导致前端无法实时收到事件。

**解决**：SSE 请求直连后端，普通 API 请求走 Next.js 代理：

```typescript
const API_BASE = "";                        // Next.js proxy
const SSE_BASE = "http://localhost:8000";    // 直连后端

export async function* streamChat(...) {
    const res = await fetch(`${SSE_BASE}/api/chat/...`, { ... });
}
```

#### 4.4 MOCK_MODE 环境变量覆盖

**问题**：系统环境变量 `OPENAI_API_KEY` 会覆盖 `.env` 文件中的值，导致 Mock 模式失效。

**解决**：在 `config.py` 中新增 `MOCK_MODE: bool = False`，`LLMProvider.is_mock` 优先检查此值：

```python
class Settings(BaseSettings):
    MOCK_MODE: bool = False
    OPENAI_API_KEY: str = ""

# llm.py
@property
def is_mock(self) -> bool:
    if settings.MOCK_MODE:
        return True
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("your-"):
        return True
    return False
```

#### 4.5 代码版本持久化与恢复

每次 `code_generated` 事件后，`chat_service` 自动保存 `CodeVersion` 到数据库：

```python
if accumulated_code:
    await save_code_version(db, project_id, accumulated_code)
    proj.status = "completed"
```

Workspace 页面加载时通过 `/latest-code` 端点恢复预览：

```typescript
const { code } = await projectApi.getLatestCode(projectId);
if (code) setPreviewHtml(code);
```

#### 4.6 Think Step — 设计文档与代码分离

**问题**：Engineer prompt 在代码前输出设计文档文本，被 `extract_html()` 误提取导致 iframe 渲染空白。

**解决**：将设计文档拆为独立 LLM 调用（Think Step），通过 `agent_stream` 事件流式显示，代码在后续 Act Step 单独生成：

```python
# Think Step: max_tokens=2048, 输出设计文档
async for chunk in agent.think(...):
    yield {"event": "agent_stream", "data": {...chunk...}}

# Act Step: max_tokens=65536, 只输出1句中文总结+代码
async for event in agent.act(...):
    yield event
```

#### 4.7 截断检测与自动续写

**问题**：大型游戏/应用代码超过 65K token 限制，LLM 输出截断导致 JS 括号不匹配、`</script>` 缺失。

**解决**：`is_js_truncated()` 检查**最后一个** `<script>` 块（非第一个，因为 Tailwind CDN config 在第一个 script 标签内），以及 HTML 结尾是否包含 `</script></body></html>`：

```python
def is_js_truncated(html: str) -> bool:
    last_script = html.rfind('<script')
    if last_script == -1: return False
    after = html[last_script:]
    return '</script>' not in after or not html.rstrip().endswith('</html>')
```

截断时调用 `_continue_code()` 将已有代码发给 LLM 续写，最多 3 次。

#### 4.8 代理环境处理

**问题**：DeepSeek API 从国内需走系统代理（`HTTP_PROXY=http://127.0.0.1:1088`），但 NVIDIA API 不需要代理。

**解决**：`main.py` 按模型选择性清除/保留代理：

```python
if "nvidia" in settings.OPENAI_BASE_URL.lower():
    for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
        os.environ.pop(key, None)
# DeepSeek 保留系统代理 — httpx trust_env=True
```

#### 4.9 agent_thinking 去重

**问题**：Engineer 模式有 Think + Act 两个步骤，同一 Agent 产生两条 `agent_thinking` 消息。

**解决**：在 SSE 流中按 agent 名称去重，同一 agent 只创建一条 thinking 消息，后续步骤的 stream 追加到同一条消息。

### 五、工程化实践

| 实践 | 具体措施 |
|------|----------|
| **类型安全** | Python: Pydantic Schema 严格类型 + 自动 API 文档；TypeScript: 全量类型定义 |
| **错误防御** | 401 自动清除 token + 引导重新登录；SSE 流错误捕获 + 友好中文提示；LLM 超时返回中文消息 |
| **截断修复** | 自动检测 JS 截断 → 3 次续写，大型项目（60K+）E2E 验证全通过 |
| **分层解耦** | Router(参数校验) → Service(业务逻辑) → Agent(智能编排) → LLM(模型调用)，每层职责清晰 |
| **优雅降级** | Mock 模式保证无 API Key 时全流程可演示；LLM 调用超时/失败时返回错误事件而非崩溃 |
| **可测试性** | 35+ 项 E2E 测试覆盖注册/登录/项目CRUD/5种模式SSE/迭代修改/版本管理/大型项目验证 |
| **Docker 化** | 多阶段构建 + 环境变量注入 + 数据卷持久化，`docker-compose up` 即用 |

### 六、与 Atoms.dev 对比

| 维度 | Atoms.dev | Atoms Demo | 差距分析 |
|------|-----------|------------|----------|
| Agent 角色数 | 7 个（含 QA/DevOps） | 8 个（Mike/Emma/Bob/Alex/Iris/Sarah/Adrian/David） | 角色更多，各有独立颜色/emoji/prompt |
| 执行模式 | 4 种（Quick/Team/Race/Research） | 5 种（+Review 审查修复） | 完全对齐且超出 |
| 可视化编辑器 | 拖拽式 Visual Editor | Monaco Editor | 这是最大差距，也是最有价值的扩展方向 |
| 代码沙箱 | Docker 容器 + 独立域名 | iframe sandbox | 安全性较弱，但 Demo 足够 |
| 部署能力 | 一键部署到 Vercel/Netlify | Deploy 按钮（生成公开URL） | 需接入真实部署 API |
| App World 社区 | 可浏览/分享生成的应用 | 无 | P2 优先级 |
| 模板系统 | 10+ 预置模板 | 8 个预置模板 | 需扩充模板库 |
| 实时协作 | WebSocket 双向通信 | SSE 单向推送 | 对 Demo 足够，生产环境需升级 |
| 截断修复 | 无公开信息 | 自动检测+3次续写 | 创新特性 |
| Think Step | 无公开信息 | 设计文档流式输出 | 透明化 AI 决策过程 |
| LLM 超时保护 | 无公开信息 | 600s超时+友好错误 | 工程健壮性 |

---

## License

[MIT](LICENSE)
