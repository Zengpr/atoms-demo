# Atoms Demo - 项目计划书

> 目标：实现一个可运行的类似 Atoms.dev 的 AI Agent 驱动式代码生成平台
> 面试岗位：深度赋智 ROOT/AI Native 全栈工程师
> 目标薪资：40k×15

---

## 一、Atoms 平台核心能力分析

### 1.1 核心功能矩阵

| 功能 | Atoms实现 | Demo实现策略 | 优先级 |
|------|-----------|-------------|--------|
| Multi-Agent工作流 | 7角色SOP协作 | 4核心Agent(PM/Arch/Eng/Leader) | P0 |
| 对话式代码生成 | 自然语言→完整Web应用 | LLM Streaming + Code Generation | P0 |
| 实时预览(App Viewer) | iframe沙箱预览 | iframe + sandbox渲染 | P0 |
| 模式切换 | Engineer/Team/Race/DeepResearch | Engineer/Team双模式 | P0 |
| 可视化编辑 | 点击元素修改 | 代码编辑器 + 热更新预览 | P1 |
| 一键部署/分享 | Atoms Cloud托管 | 预览链接分享 | P1 |
| 用户系统 | 注册/登录/Credit | JWT Auth + SQLite | P0 |
| 项目管理 | 项目列表/历史 | CRUD + 版本历史 | P0 |
| 后端集成 | Atoms Cloud/Supabase | 内置轻量BaaS | P2 |
| Race Mode | 多模型竞速 | 并行调用多模型对比 | P1 |

### 1.2 关键交互流程

```
用户注册/登录 → 创建项目 → 选择模式(Engineer/Team)
→ 输入自然语言需求 → Agent协作(SOP工作流)
→ 实时显示Agent思考/执行过程 → 代码生成
→ App Viewer实时预览 → 迭代修改 → 发布/分享
```

---

## 二、技术选型

### 2.1 前端
- **框架**: Next.js 14 (App Router) + React 18
- **UI**: Tailwind CSS + shadcn/ui + Framer Motion
- **代码编辑器**: Monaco Editor
- **预览**: iframe sandbox
- **状态管理**: Zustand
- **实时通信**: WebSocket (Agent执行过程流式展示)

### 2.2 后端
- **语言**: Python (FastAPI) — 快速开发，LLM生态丰富
- **LLM编排**: LangChain / 直接调用 OpenAI API
- **流式输出**: SSE (Server-Sent Events)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy
- **认证**: JWT
- **文件存储**: 本地文件系统

### 2.3 部署
- **前端**: Vercel
- **后端**: Railway / Fly.io
- **整体**: Docker Compose 一键启动

---

## 三、系统架构

```
┌─────────────────────────────────────────────────┐
│                    Frontend                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Chat UI │ │ Preview  │ │  Code Editor     │ │
│  │  Panel   │ │ Panel    │ │  Panel           │ │
│  └────┬─────┘ └────┬─────┘ └───────┬──────────┘ │
│       │             │               │            │
│  ┌────┴─────────────┴───────────────┴──────────┐ │
│  │           Zustand State Store               │ │
│  └────────────────────┬────────────────────────┘ │
└───────────────────────┼──────────────────────────┘
                        │ HTTP/SSE/WS
┌───────────────────────┼──────────────────────────┐
│                   Backend (FastAPI)               │
│  ┌──────────┐ ┌──────┴──────┐ ┌───────────────┐ │
│  │ Auth API │ │ Chat/Agent  │ │ Project API   │ │
│  │          │ │ SSE Stream  │ │               │ │
│  └────┬─────┘ └──────┬──────┘ └───────┬───────┘ │
│       │              │                │          │
│  ┌────┴──────────────┴────────────────┴───────┐ │
│  │          Agent Orchestrator                 │ │
│  │  ┌─────────┐ ┌─────────┐ ┌───────────┐    │ │
│  │  │ Leader  │ │   PM    │ │ Architect │    │ │
│  │  │ Agent   │ │ Agent   │ │ Agent     │    │ │
│  │  └─────────┘ └─────────┘ └───────────┘    │ │
│  │  ┌─────────┐ ┌─────────┐                  │ │
│  │  │ Engineer│ │ Research│                  │ │
│  │  │ Agent   │ │ Agent   │                  │ │
│  │  └─────────┘ └─────────┘                  │ │
│  └──────────────────┬────────────────────────┘ │
│                     │                           │
│  ┌──────────────────┴────────────────────────┐ │
│  │           LLM Provider Layer              │ │
│  │   OpenAI GPT-4 / Claude / DeepSeek        │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────┐  ┌──────────┐  ┌────────────┐  │
│  │  SQLite/   │  │ File     │  │  Project   │  │
│  │ PostgreSQL │  │ Storage  │  │  Sandbox   │  │
│  └────────────┘  └──────────┘  └────────────┘  │
└──────────────────────────────────────────────────┘
```

---

## 四、功能模块开发计划

### Phase 1: 基础框架搭建 (2h)
- [x] 项目初始化 (Next.js + FastAPI)
- [ ] 数据库Schema设计与Migration
- [ ] 用户认证系统 (注册/登录/JWT)
- [ ] 基础UI布局 (三栏式: Chat + Preview + Editor)

### Phase 2: 核心Agent系统 (3h)
- [ ] Agent基类与接口设计
- [ ] Leader Agent (任务分解与协调)
- [ ] PM Agent (需求分析，PRD生成)
- [ ] Architect Agent (技术方案设计)
- [ ] Engineer Agent (代码生成)
- [ ] Agent SOP工作流编排
- [ ] SSE流式输出Agent思考过程

### Phase 3: 对话与代码生成 (2h)
- [ ] 对话界面 (ChatGPT风格)
- [ ] 代码生成Pipeline (Prompt→Agent→Code)
- [ ] 生成代码的沙箱预览 (iframe)
- [ ] 模式切换 (Engineer/Team)

### Phase 4: 项目管理与持久化 (1h)
- [ ] 项目CRUD
- [ ] 对话历史持久化
- [ ] 生成代码版本管理
- [ ] 项目分享链接

### Phase 5: 延展能力 (1h)
- [ ] Race Mode (多模型并行对比)
- [ ] 可视化编辑 (Monaco Editor集成)
- [ ] Deep Research Agent
- [ ] 模板市场 (预置模板)

### Phase 6: 部署与文档 (1h)
- [ ] Docker化
- [ ] Vercel/Railway部署
- [ ] 说明文档撰写
- [ ] GitHub整理

---

## 五、数据库Schema

### users
- id, email, username, password_hash, avatar, credits, created_at, updated_at

### projects
- id, user_id, name, description, mode(engineer/team), status, thumbnail, created_at, updated_at

### conversations
- id, project_id, mode, created_at

### messages
- id, conversation_id, role(user/assistant/agent), agent_name, content, metadata, created_at

### code_versions
- id, project_id, version, code_html, code_css, code_js, created_at

### agent_logs
- id, conversation_id, agent_name, action, input, output, duration_ms, created_at

---

## 六、核心创新点（差异化亮点）

1. **可视化Agent SOP流程图**: 实时展示Agent间的协作流程，用户能看到任务如何在Agent间流转
2. **Race Mode**: 并行调用多个LLM，用户选择最佳结果
3. **渐进式代码生成**: 不是一次性生成全部代码，而是分步骤(架构→页面→组件→样式)逐步构建，每步可预览
4. **Code Diff可视化**: 迭代修改时展示代码变更差异
5. **模板衍生**: 从一个模板快速衍生出新项目

---

## 七、开发进度追踪

| Phase | 状态 | 开始时间 | 完成时间 |
|-------|------|---------|---------|
| Phase 1 | 🔄 进行中 | - | - |
| Phase 2 | ⏳ 待开始 | - | - |
| Phase 3 | ⏳ 待开始 | - | - |
| Phase 4 | ⏳ 待开始 | - | - |
| Phase 5 | ⏳ 待开始 | - | - |
| Phase 6 | ⏳ 待开始 | - | - |
