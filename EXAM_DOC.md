# ROOT 全栈岗位笔试 —— 曾培润

## 实现说明

### 项目概述

Atoms Demo 是一个受 Atoms.dev 启发的 AI Agent 驱动代码生成平台。用户通过自然语言描述需求，多个专业化 AI Agent 以 SOP 工作流协同完成从需求分析、架构设计到代码实现的全流程，并通过 SSE 实时流式展示 Agent 的思考与执行过程，生成的代码在 iframe 沙箱中即时预览。

- **Demo 链接 (Railway)**: https://frontend-production-f189.up.railway.app（国内直连可用）
- **Demo 链接 (Vercel)**: https://frontend-theta-inky-12.vercel.app（国内需 VPN）
- **后端 API**: https://backend-production-e62a.up.railway.app/docs
- **GitHub**: https://github.com/Zengpr/atoms-demo (commit: 04424ed)
- **测试账号**: `demo@atoms.dev` / `Atoms2024!`（注册即用，无需额外 API Key）

### 架构设计

#### 分层架构

```
Frontend (Next.js 16 + React 19)
  ├── Pages: Login / Dashboard / Workspace (Chat+Preview+Editor 三栏)
  ├── State: Zustand (Auth / Project / Chat / Preview 四 Store)
  └── UI: Tailwind CSS + Framer Motion + Monaco Editor

Backend (Python FastAPI)
  ├── Routers: Auth / Projects / Chat(SSE) / Preview
  ├── Services: 认证 / 对话管理 / 项目管理
  ├── Agents: 5 个专业化角色 (Mike/Emma/Bob/Alex/Iris)
  ├── Orchestrator: 4 种执行模式路由 + SSE 事件编排
  └── LLM: OpenAI-compatible API (Agnes AI 2.0 Flash)

Database: SQLite (WAL 模式, 可迁移至 PostgreSQL)
Deploy: Vercel (前端) + Railway (后端)
```

#### SSE 事件协议

5 种标准事件覆盖 Agent 执行全生命周期：

| 事件 | 说明 |
|------|------|
| `agent_thinking` | Agent 开始思考，显示 spinner |
| `agent_stream` | 思考过程文本片段（打字机效果） |
| `agent_action` | Agent 完成一步操作 |
| `code_generated` | 完整代码生成 |
| `message_complete` | 整轮对话结束 |

#### 4 种执行模式

| 模式 | 流程 | 适用场景 |
|------|------|----------|
| Engineer | 单 Agent 快速生成 | 简单应用、需求明确 |
| Team | Mike→Emma→Bob→Alex 四 Agent SOP | 复杂应用、需需求分析 |
| Race | 同模型不同 Prompt 并行 | 创意类、需多方案对比 |
| Research | Iris 深度研究 | 技术调研、方案评估 |

### 完成范围

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户注册/登录/JWT 认证 | ✅ | bcrypt 密码哈希 + 7天 Token |
| 项目 CRUD + 版本管理 | ✅ | 创建/列表/详情/删除 + 代码版本快照 |
| Engineer / Team / Race / Research 4 种模式 | ✅ | 全部实现，SSE 流式输出 |
| iframe 实时预览 | ✅ | PC/Tablet/Mobile 视口切换 |
| Monaco Editor 代码编辑 | ✅ | 可编辑并实时同步预览 |
| 迭代修改 | ✅ | 基于对话历史 + 上次代码上下文增量修改 |
| 数据持久化 | ✅ | 刷新后项目、对话、代码、Preview 均保留 |
| Console 错误反馈 | ✅ | iframe 错误捕获并传给 AI 修复 |
| 暗色主题 UI | ✅ | Framer Motion 动画 + Design Token |
| Docker Compose 一键部署 | ✅ | `docker-compose up` 即用 |
| 线上 Demo 可用 | ✅ | 无需 API Key，注册即用 |
| Lint 检查 | ✅ | 0 error, 0 warning |

### 已知限制

1. **SQLite 并发**: 使用 WAL 模式 + busy_timeout 缓解，但高并发场景仍需迁移 PostgreSQL
2. **iframe 沙箱**: 键盘交互受限（sandbox 安全策略），游戏类应用体验欠佳
3. **Vercel 域名**: `vercel.app` 在中国大陆被 DNS 污染，推荐使用 Railway 域名 `frontend-production-f189.up.railway.app`
4. **代码沙箱**: iframe 方案安全性弱于 Docker 容器隔离
5. **Deploy 按钮**: 为占位功能，未接入真实部署 API
6. **Race 模式**: 当前用同一模型不同 Prompt 策略，未实现跨模型对比

### E2E 测试结果

**18/18 全通过 (100%)**

| 分类 | 测试项 | 结果 |
|------|--------|------|
| 前端 | Homepage / Login / Dashboard 三页面加载 | ✅✅✅ |
| 认证 | Register / Login / Auth me | ✅✅✅ |
| 项目 | Create / List | ✅✅ |
| Chat SSE | HTML生成(20KB+) / 5种SSE事件 / 代码持久化 / 迭代修改 / Preview / History | ✅✅✅✅✅✅ |
| 跨域 | CORS allows frontend (*) | ✅ |
| 持久化 | Projects persist after re-login | ✅ |
| Demo账号 | demo@atoms.dev 登录 | ✅ |

**后端 API 专项测试**: 29/29 PASS（health/register/login/demo/CRUD/SSE/Agent/代码持久化/版本/迭代/history/preview/CORS）

**核心功能验证（HR 5项）**:

| 测试项 | 结果 | 说明 |
|--------|------|------|
| 生成计算器 | ✅ | 20KB+ HTML, SSE 流式, 5种事件 |
| 生成另一类应用 | ✅ | Engineer/Team/Race/Research 全模式可用 |
| 同项目迭代修改 | ✅ | 代码变更确认 changed=True |
| 修复 Bug | ✅ | 基于历史上下文修复 |
| 刷新后数据保留 | ✅ | 项目/对话/代码/Preview 全持久化 |

### 关键技术决策

1. **FastAPI (Python)** 而非 Go/Node.js：LLM 生态原生 Python SDK，Agent prompt 构建极灵活
2. **SSE** 而非 WebSocket：单向推送天然适配，实现更简单，自动重连
3. **SQLite** 而非 PostgreSQL：Demo 零配置优先，WAL 模式 + SQLAlchemy 抽象可平滑迁移
4. **OpenAI-compatible API**：三参数切换模型（BASE_URL + API_KEY + MODEL），零代码改动
5. **Zustand** 而非 Redux：轻量级，4 个独立 Store 职责清晰，无 boilerplate

---

*提交时间: 2026-07-25 | GitHub commit: 04424ed*
