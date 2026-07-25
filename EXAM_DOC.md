# ROOT 全栈岗位笔试 —— 曾培润

## 实现说明

### 项目概述

Atoms Demo 是一个受 Atoms.dev 启发的 AI Agent 驱动代码生成平台。用户通过自然语言描述需求，多个专业化 AI Agent 以 SOP 工作流协同完成从需求分析、架构设计到代码实现的全流程，并通过 SSE 实时流式展示 Agent 的思考与执行过程，生成的代码在 iframe 沙箱中即时预览。

- **Demo 链接 (Railway)**: https://frontend-production-f189.up.railway.app（国内直连可用）
- **Demo 链接 (Vercel)**: https://frontend-theta-inky-12.vercel.app（国内需 VPN）
- **后端 API**: https://backend-api-production-8923.up.railway.app/docs
- **GitHub**: https://github.com/Zengpr/atoms-demo (commit: e514d07)
- **测试账号**: `demo@atoms.dev` / `Atoms2024!`（注册即用，无需额外 API Key）

### 架构设计

#### 分层架构

```
Frontend (Next.js 16 + React 19)
  ├── Pages: Login / Dashboard / Workspace (Chat+Preview+Editor+Versions 四面板)
  ├── State: Zustand (Auth / Project / Chat / Preview 四 Store)
  └── UI: Tailwind CSS + Framer Motion + Monaco Editor

Backend (Python FastAPI)
  ├── Routers: Auth / Projects / Chat(SSE) / Preview / Templates
  ├── Services: 认证 / 对话管理 / 项目管理
  ├── Agents: 5 个专业化角色 (Mike/Emma/Bob/Alex/Iris)
  ├── Orchestrator: 计划驱动编排 + Human-in-the-loop + SSE 事件流
  └── LLM: OpenAI-compatible API (Agnes AI / NVIDIA)

Database: SQLite (WAL 模式, 可迁移至 PostgreSQL)
Deploy: Railway (前端+后端) / Vercel (前端)
```

#### SSE 事件协议

6 种标准事件覆盖 Agent 执行全生命周期：

| 事件 | 说明 |
|------|------|
| `agent_thinking` | Agent 开始思考，显示 spinner |
| `agent_stream` | 思考过程文本片段（打字机效果） |
| `agent_action` | Agent 完成一步操作（含 PRD/架构/计划数据） |
| `approval_request` | Human-in-the-loop 确认点，用户可审批后继续 |
| `code_generated` | 完整代码生成 |
| `message_complete` | 整轮对话结束 |

#### 5 种执行模式

| 模式 | 流程 | 适用场景 |
|------|------|----------|
| Engineer | Alex 单 Agent 快速生成 | 简单应用、需求明确 |
| Team | Mike制定计划→审批→按计划动态执行各Agent | 复杂应用、需需求分析+架构设计 |
| Race | Strategy A + Strategy B 并行生成 | 创意类、需多方案对比 |
| Research | Iris 深度研究 | 技术调研、方案评估 |
| Review | Iris审查代码→Alex修复改进 | 代码审查、Bug修复 |

### 核心亮点（对照 Atoms.dev）

| Atoms 特性 | 实现方式 | 说明 |
|------------|---------|------|
| Named Agent Personas | 5个Agent各有名字/emoji/角色/独立prompt | Mike👨‍💼/Emma👩‍💻/Bob🏗️/Alex💻/Iris🔬 |
| Multi-Agent SOP | Leader计划驱动编排，非硬编码pipeline | Mike分析需求→制定计划→按计划分配Agent |
| Human-in-the-loop | approval_request事件+前端确认按钮 | 每步Agent完成后请求用户确认再继续 |
| Agent上下文传递 | PRD/架构文档自动传递给下游Agent | PM产出→Architect参考→Engineer实现 |
| 模板/Remix | 8个模板一键创建项目 | Landing/Dashboard/E-commerce/Portfolio/Calculator/Todo/2048/Snake |
| 版本历史+回滚 | 代码版本列表+一键Restore | 每次生成自动保存版本，支持回滚到任意版本 |
| 真实Deploy | 生成公开可访问URL | /api/preview/public/{page_id} 无需登录 |
| 迭代增强 | 完整代码上下文（非截断） | 修改时传入完整代码+对话历史+console错误 |
| Live Preview | iframe + PC/Tablet/Mobile视口 | Console错误捕获→自动反馈给AI修复 |
| 5种模式 | Engineer/Team/Race/Research/Review | 覆盖从快速生成到深度审查的全部场景 |

### 完成范围

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户注册/登录/JWT 认证 | ✅ | bcrypt 密码哈希 + 7天 Token |
| 项目 CRUD + 版本管理 | ✅ | 创建/列表/详情/删除 + 代码版本快照 |
| Engineer/Team/Race/Research/Review 5 种模式 | ✅ | 全部实现，SSE 流式输出 |
| 计划驱动的Agent编排 | ✅ | Leader分析→制定计划→按步骤分配Agent |
| Human-in-the-loop | ✅ | 每步Agent完成后审批确认再继续 |
| 模板/Remix系统 | ✅ | 8个预置模板 + 后端Templates API |
| 版本历史UI + 一键回滚 | ✅ | Versions标签页 + Restore API |
| 真实Deploy | ✅ | 生成公开URL，无需登录即可访问 |
| iframe 实时预览 | ✅ | PC/Tablet/Mobile 视口切换 |
| Monaco Editor 代码编辑 | ✅ | 可编辑并实时同步预览 |
| 迭代修改(完整代码上下文) | ✅ | 传入完整代码+历史+PRD+架构+console错误 |
| 数据持久化 | ✅ | 刷新后项目、对话、代码、Preview 均保留 |
| Console 错误反馈 | ✅ | iframe 错误捕获并传给 AI 修复 |
| 暗色主题 UI | ✅ | Framer Motion 动画 + Design Token |
| Docker 部署 | ✅ | Dockerfile + docker-compose |
| 线上 Demo 可用 | ✅ | 无需 API Key，注册即用 |

### 已知限制

1. **SQLite 并发**: 使用 WAL 模式 + busy_timeout 缓解，高并发需迁移 PostgreSQL
2. **iframe 沙箱**: 键盘交互受限（sandbox 安全策略），游戏类应用体验欠佳
3. **Vercel 域名**: `vercel.app` 在中国大陆被 DNS 污染，推荐使用 Railway 域名
4. **Deploy 持久化**: 公开页面存内存，服务重启后丢失（可改用对象存储）
5. **Race 模式**: 当前用同一模型不同 Prompt 策略，未实现跨模型对比

### E2E 测试结果

**线上测试 18/18 (100%)** + **本地新功能测试 10/10 (100%)**

线上（旧版功能）：

| 分类 | 测试项 | 结果 |
|------|--------|------|
| 前端 | Homepage / Login / Dashboard 三页面加载 | ✅✅✅ |
| 认证 | Register / Login / Auth me | ✅✅✅ |
| 项目 | Create / List | ✅✅ |
| Chat SSE | HTML生成(20KB+) / 5种SSE事件 / 代码持久化 / 迭代修改 / Preview / History | ✅✅✅✅✅✅ |
| 跨域 | CORS allows frontend (*) | ✅ |
| 持久化 | Projects persist after re-login | ✅ |
| Demo账号 | demo@atoms.dev 登录 | ✅ |

本地（新功能）：

| 测试项 | 结果 | 说明 |
|--------|------|------|
| Templates API | ✅ | 8个模板，含icon/name/description/mode |
| Engineer SSE (mock) | ✅ | 4种SSE事件+代码生成 |
| 版本历史 | ✅ | 自动创建版本快照 |
| Deploy | ✅ | 返回公开URL+page_id |
| 公开页面访问 | ✅ | 无需登录即可查看 |
| Team approval_request | ✅ | human-in-the-loop确认事件 |
| Team 计划生成 | ✅ | Leader产出Team plan |
| 版本回滚 | ✅ | Restore API恢复旧版本 |
| 版本回滚后代码更新 | ✅ | preview更新为回滚版本 |

**核心功能验证（HR 5项）**:

| 测试项 | 结果 | 说明 |
|--------|------|------|
| 生成计算器 | ✅ | 20KB+ HTML, SSE 流式, 5种事件 |
| 生成另一类应用 | ✅ | 5种模式全可用，Team含审批流程 |
| 同项目迭代修改 | ✅ | 完整代码上下文，AI理解PRD+架构后修改 |
| 修复 Bug | ✅ | Console错误→AI修复→Preview刷新 |
| 刷新后数据保留 | ✅ | 项目/对话/代码/版本 全持久化 |

### 关键技术决策

1. **FastAPI (Python)** 而非 Go/Node.js：LLM 生态原生 Python SDK，Agent prompt 构建极灵活
2. **计划驱动编排** 而非硬编码pipeline：Leader分析需求制定计划，按计划动态分配Agent，而非固定的 PM→Architect→Engineer 顺序
3. **Human-in-the-loop** 而非全自主：每步Agent完成后请求用户确认，避免Agent runaway
4. **SSE** 而非 WebSocket：单向推送天然适配，实现更简单，自动重连
5. **SQLite** 而非 PostgreSQL：Demo零配置优先，WAL模式+SQLAlchemy抽象可平滑迁移
6. **OpenAI-compatible API**：三参数切换模型（BASE_URL + API_KEY + MODEL），零代码改动
7. **Zustand** 而非 Redux：轻量级，4个独立Store职责清晰，无boilerplate

### 如果继续投入时间

| 优先级 | 扩展方向 | 说明 |
|--------|---------|------|
| P0 | PostgreSQL迁移 | SQLAlchemy抽象已就绪，换连接字符串即可 |
| P0 | GitHub连接Railway自动部署 | push→自动构建，解决当前手动部署问题 |
| P1 | @-mention指定Agent | 用户可通过@Alex直接指定Agent |
| P1 | Agent DAG可视化 | 当前Timeline→升级为流程图+实时进度 |
| P1 | Visual Editor | 点击预览元素→侧边栏编辑属性 |
| P2 | 跨模型Race | 接入Claude/GPT/DeepSeek多模型对比 |
| P2 | 对象存储Deploy | S3/R2持久化公开页面 |
| P3 | 多会话/项目Fork | 每项目多Conversation + 社区App World |

---

*提交时间: 2026-07-25 | GitHub commit: e64a43f*
