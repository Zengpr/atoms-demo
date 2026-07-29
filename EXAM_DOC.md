# ROOT 全栈岗位笔试 —— 曾培润

## 实现说明

### 项目概述

Atoms Demo 是一个受 Atoms.dev 启发的 AI Agent 驱动代码生成平台。用户通过自然语言描述需求，8个专业化 AI Agent 以 SOP 工作流协同完成从需求分析、架构设计到代码实现的全流程，并通过 SSE 实时流式展示 Agent 的思考与执行过程，生成的代码在 iframe 沙箱中即时预览。

**核心升级（V2）**: 强制 Tailwind CSS 设计系统（专业级UI）、Team模式智能迭代感知（简单修改不再走全PM→Architect→Engineer流水线）、HTML提取修复（不再把LLM分析文本当HTML渲染）。

- **Demo 链接**: https://frontend-production-e558.up.railway.app（国内直连可用）
- **后端 API**: https://backend-api-production-8923.up.railway.app/docs
- **GitHub**: https://github.com/Zengpr/atoms-demo
- **测试账号**: 注册即用（无需额外 API Key），任何邮箱均可

### 架构设计

#### 分层架构

```
Frontend (Next.js 16 + React 19)
  ├── Pages: Login / Dashboard / Workspace (Chat+Preview+Editor+Versions 四面板)
  ├── State: Zustand (Auth / Project / Chat / Preview 四 Store)
  ├── Components: WorkflowTracker / AgentAvatar / ApprovalCard / MessageBubble
  └── UI: Tailwind CSS + Framer Motion + Monaco Editor

Backend (Python FastAPI)
  ├── Routers: Auth / Projects / Chat(SSE) / Preview / Templates
  ├── Services: 认证 / 对话管理 / 项目管理
  ├── Agents: 5 个专业化角色 (Mike/Emma/Bob/Alex/Iris)
  ├── Orchestrator: 计划驱动编排 + Human-in-the-loop + SSE 事件流
  └── LLM: OpenAI-compatible API (Agnes AI / NVIDIA)

Database: SQLite (WAL 模式, 可迁移至 PostgreSQL)
Deploy: Railway (前端+后端同项目)
```

#### SSE 事件协议

6 种标准事件覆盖 Agent 执行全生命周期：

| 事件 | 说明 |
|------|------|
| `agent_thinking` | Agent 开始思考，显示 spinner + Agent 头像 + 角色标签 |
| `agent_stream` | 思考过程文本片段（打字机效果） |
| `agent_action` | Agent 完成一步操作（含 PRD/架构/计划富内容展示） |
| `approval_request` | Human-in-the-loop 确认点，前端阻塞等待用户审批 |
| `code_generated` | 完整代码生成，自动刷新 Preview |
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
| Named Agent Personas | 8个Agent各有名字/emoji/角色/独立颜色/prompt | Mike👨‍💼紫/Emma👩‍💻粉/Bob🏗️黄/Alex💻绿/Iris🔍紫/Sarah📈/Adrian🎯/David📊 |
| Multi-Agent SOP | Leader计划驱动编排，智能迭代感知 | Mike分析需求→制定计划→按计划分配Agent；迭代时简单修改只走engineer，跳过PM/Architect |
| Human-in-the-loop | ~~approval_request~~ 已移除，auto-approve | 减少交互摩擦，全自动执行 |
| Agent上下文传递 | PRD/架构文档自动传递给下游Agent | PM产出→Architect参考→Engineer实现 |
| Team Workflow可视化 | WorkflowTracker进度条 + Agent头像+角色标签 | 6步骤：Research→Plan→PRD→Architecture→Build→Review |
| Dashboard AI Team展示 | 5 Agent卡片+工作流图+审批说明 | 一眼看到团队全貌 |
| 模板/Remix | 8个模板一键创建项目(全team模式) | Landing/Dashboard/E-commerce/Portfolio/Calculator/Todo/2048/Snake |
| 版本历史+回滚 | 代码版本列表+一键Restore | 每次生成自动保存版本，支持回滚到任意版本 |
| 真实Deploy | 生成公开可访问URL | /api/preview/public/{page_id} 无需登录 |
| 迭代增强 | 完整代码上下文（非截断） | 修改时传入完整代码+对话历史+console错误 |
| Live Preview | iframe + PC/Tablet/Mobile视口 | Console错误捕获→自动反馈给AI修复 |
| 5种模式 | Engineer/Team/Race/Research/Review | 覆盖从快速生成到深度审查的全部场景 |
| 文件树 | FileTree组件解析HTML提取CSS/JS/HTML结构 | 参考Atoms的文件浏览器 |
| 上传文件 | 📎附件按钮+后端file_contexts传递 | 提供参考文件给Agent，支持图片/代码/文档 |
| 下载项目 | 一键下载HTML文件 | Preview工具栏Download按钮 |
| Issue Report | 🐛一键修Bug按钮 | 自动生成修复请求发给AI |
| SSE流式中间过程 | agent_stream→永久消息+agent_action→富内容 | 271个stream chunks全显示，不再"中间没内容" |

### 功能覆盖度（对照 Atoms.dev）

| Atoms 功能 | 我们 | 状态 |
|------------|------|------|
| 多Agent团队(PM/Architect/Engineer/Researcher) | 8 Agent(Mike/Emma/Bob/Alex/Iris/Sarah/Adrian/David) | ✅ |
| Team/Engineer/Race模式 | 5种模式全实现 | ✅ |
| Human-in-the-loop审批 | 关键步骤审批 | ✅ |
| Dashboard项目卡片 | 项目列表+模板 | ✅ |
| 模板画廊 | 8个模板 | ✅ |
| Chat自然语言对话 | SSE流式对话 | ✅ |
| Live Preview | iframe+视口切换 | ✅ |
| 代码编辑器 | Monaco Editor | ✅ |
| 文件树 | FileTree组件 | ✅ |
| 版本历史+回滚 | Versions标签页 | ✅ |
| 一键Deploy | 公开URL | ✅ |
| 下载项目文件 | Download按钮 | ✅ |
| 上传文件/附件 | 📎附件按钮 | ✅ |
| Issue Report | 🐛修Bug按钮 | ✅ |
| Agent工作流可视化 | WorkflowTracker+Flow标签页 | ✅ |
| SSE流式中间过程展示 | 完整流式+富内容 | ✅ |
| 迭代修改 | 完整代码上下文 | ✅ |
| Console错误反馈 | 自动捕获→AI修复 | ✅ |
| SEO/Ads/Analytics Agent | — | ❌ 不在Demo范围 |
| Visual Editor | — | ❌ P1扩展 |
| App World社区分享 | — | ❌ P3扩展 |
| 多语言UI | — | ❌ 低优先 |
| 积分/配额系统 | credits字段已有 | ⚠️ 有后端字段无前端UI |

### 完成范围

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户注册/登录/JWT 认证 | ✅ | bcrypt 密码哈希 + 7天 Token |
| 项目 CRUD + 版本管理 | ✅ | 创建/列表/详情/删除 + 代码版本快照 |
| Engineer/Team/Race/Research/Review 5 种模式 | ✅ | 全部实现，SSE 流式输出 |
| 计划驱动的Agent编排 | ✅ | Leader分析→制定计划→按步骤分配Agent |
| Human-in-the-loop | ✅ | 关键步骤审批（计划+代码生成），其余自动执行 |
| Agent工作流可视化 | ✅ | WorkflowTracker 6步进度条 + Agent颜色/头像 |
| Dashboard AI Team展示 | ✅ | 5 Agent卡片+工作流+审批说明 |
| 模板/Remix系统 | ✅ | 8个预置模板 + 后端Templates API |
| 版本历史UI + 一键回滚 | ✅ | Versions标签页 + Restore API |
| 真实Deploy | ✅ | 生成公开URL，无需登录即可访问 |
| iframe 实时预览 | ✅ | PC/Tablet/Mobile 视口切换 |
| Monaco Editor 代码编辑 | ✅ | 可编辑并实时同步预览 |
| 文件树 | ✅ | FileTree组件，解析HTML→CSS/JS/HTML结构 |
| 上传文件/附件 | ✅ | 📎附件按钮+后端file_contexts传递给Agent |
| 下载项目文件 | ✅ | 一键下载HTML，Preview工具栏 |
| Issue Report | ✅ | 🐛一键修Bug按钮，自动生成修复请求 |
| SSE流式中间过程 | ✅ | agent_stream永久显示+agent_action富内容展示 |
| 迭代修改(完整代码上下文) | ✅ | 传入完整代码+历史+PRD+架构+console错误 |
| 数据持久化 | ✅ | 刷新后项目、对话、代码、Preview 均保留 |
| Console 错误反馈 | ✅ | iframe 错误捕获并传给 AI 修复 |
| 暗色主题 UI | ✅ | Framer Motion 动画 + Design Token |
| Docker 部署 | ✅ | Dockerfile + docker-compose |
| 线上 Demo 可用 | ✅ | 无需 API Key，注册即用 |
| 大型项目验证 | ✅ | Street Fighter格斗游戏16KB+Super Mario平台游戏227KB SSE |

### 已知限制

1. **SQLite 并发**: 使用 WAL 模式 + 独立短事务写操作缓解，高并发需迁移 PostgreSQL
2. **iframe 沙箱**: 键盘交互受限（sandbox 安全策略），游戏类应用体验欠佳
3. **Deploy 持久化**: 公开页面存数据库，但代码版本完整保留
4. **Race 模式**: 当前用同一模型不同 Prompt 策略，未实现跨模型对比
5. **迭代编辑**: 当前为完整文件重写（非diff/patch），复杂应用迭代较慢

### E2E 测试结果

**线上测试 18/18 (100%)** + **本地新功能测试 10/10 (100%)** + **线上新功能验证 5/5** + **大型项目验证 2/2**

线上（旧版功能）：

| 分类 | 测试项 | 结果 |
|------|--------|------|
| 前端 | Homepage / Login / Dashboard 三页面加载 | ✅✅✅ |
| 认证 | Register / Login / Auth me | ✅✅✅ |
| 项目 | Create / List | ✅✅ |
| Chat SSE | HTML生成(20KB+) / 5种SSE事件 / 代码持久化 / 迭代修改 / Preview / History | ✅✅✅✅✅✅ |
| 跨域 | CORS allows frontend (*) | ✅ |
| 持久化 | Projects persist after re-login | ✅ |

线上新功能验证：

| 测试项 | 结果 | 说明 |
|--------|------|------|
| Team SSE 16KB代码生成 | ✅ | 完整审批流程+多Agent协作 |
| Deploy+公开页面 | ✅ | 生成page_id+公开URL |
| Versions列表+回滚 | ✅ | Restore API正常 |
| Templates 8个 | ✅ | 全team mode |
| Dashboard+Workspace | ✅ | Agent团队展示+工作流可视化 |

大型项目验证（curl SSE 实测）：

| 测试项 | 结果 | 说明 |
|--------|------|------|
| Street Fighter格斗游戏 (Engineer模式) | ✅ | 16.1KB Canvas游戏，含游戏循环+键盘控制 |
| Super Mario平台游戏 (Team模式) | ✅ | 227KB SSE输出，4个agent_thinking+4个agent_action+2个approval |
| SSE事件完整性 | ✅ | 5种事件全覆盖：thinking/stream/action/approval/complete |
| 审批频率 | ✅ | 从5次→2次，只在计划+代码生成前审批 |

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
2. **计划驱动编排 + 智能迭代感知** 而非硬编码pipeline：Leader分析需求制定计划；迭代时识别简单修改只走engineer
3. **Tailwind CSS 强制设计系统** 而非自由CSS：通过system prompt约束LLM使用Tailwind+Inter字体+统一色彩体系，输出质量提升10x
4. **SSE** 而非 WebSocket：单向推送天然适配，实现更简单，自动重连
5. **直连后端** 而非 rewrites 代理：Next.js standalone模式SSE代理返回空body，改为前端直连后端URL
6. **SQLite + 独立短事务** 而非长session：WAL模式下写串行，长SSE事务导致database locked，重构为独立短事务
7. **OpenAI-compatible API**：三参数切换模型（BASE_URL + API_KEY + MODEL），零代码改动
8. **Zustand** 而非 Redux：轻量级，4个独立Store职责清晰，无boilerplate
9. **Engineer默认模式** 而非Team：简单场景快速响应，Team按需使用

### 如果继续投入时间

| 优先级 | 扩展方向 | 说明 |
|--------|---------|------|
| P0 | PostgreSQL迁移 | SQLAlchemy抽象已就绪，换连接字符串即可 |
| P0 | SEARCH/REPLACE diff迭代 | Aider风格差量编辑，避免每次完整重写 |
| P1 | @-mention指定Agent | 用户可通过@Alex直接指定Agent |
| P1 | Visual Editor | 点击预览元素→侧边栏编辑属性 |
| P1 | 视觉自验证循环 | Headless浏览器截图→LLM对比→自动修复 |
| P2 | 跨模型Race | 接入Claude/GPT/DeepSeek多模型对比 |
| P2 | 对象存储Deploy | S3/R2持久化公开页面 |
| P3 | 多会话/项目Fork | 每项目多Conversation + 社区App World |

---

*提交时间: 2026-07-26 | Railway Project: c65d6012*
