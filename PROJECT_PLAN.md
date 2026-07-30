# Atoms Demo — Project Improvement Plan

## Context
- **Goal**: Build a polished, production-quality AI Agent code generation platform demo for 深度赋智 (ROOT) full-stack engineer interview
- **Reference**: Atoms.dev (8 specialized agents, SOP collaboration, visual editor, Atoms Cloud)
- **Deadline**: ASAP — 48h from task receipt
- **Stakes**: 40k×15 salary position

---

## Phase 0: Critical Bug Fixes (MUST DO FIRST)

### P0-1: Fix html_utils.py — Don't return raw text as HTML ✅ DONE
- **Root Cause**: `extract_html()` at line 26-28 treats ANY text containing `<div>` or `<body>` as HTML
- **Effect**: When LLM outputs analysis text before code (e.g., "1. **Analysis** — <div> structure..."), the ENTIRE response including analysis is rendered as broken HTML → "layout disorder"
- **Fix**: Only extract content between `<!DOCTYPE html>` or `<html>` tags; strip anything before the HTML start tag
- **File**: `backend/app/utils/html_utils.py:26-28`

### P0-2: Rewrite Engineer Agent Prompt ✅ DONE
- **Root Cause**: 
  1. Contradictory instructions: "Do NOT explain" (line 39) vs "Output Analysis/Design/Implementation" (line 179)
  2. No design system mandated — LLM invents generic inline styles → ugly output
  3. Over-indexed on game requirements (50% of prompt is game-specific)
  4. Iteration = full rebuild instead of targeted edit
- **Fix**:
  1. MANDATE Tailwind CSS via CDN + Inter font + specific design specs
  2. Remove Analysis/Design/Implementation format — just output code
  3. Add professional UI checklist (spacing, shadows, hover states, responsive)
  4. For iteration: instruct LLM to make targeted changes, output full file but with minimal changes
- **File**: `backend/app/agents/engineer.py`

### P0-3: Fix Team Mode Iteration Awareness ✅ DONE
- **Root Cause**:
  1. Leader has no iteration context — never sees `previous_code` or `is_iteration`
  2. Leader fallback is hardcoded PM→Architect→Engineer even for "make button blue"
  3. `is_iteration` not set in team mode context
- **Fix**:
  1. Pass `is_iteration` and `previous_code` to leader's think prompt
  2. Instruct leader: for simple iterations, assign ONLY engineer (skip PM/Architect)
  3. Set `context["is_iteration"]` in orchestrator for team mode
- **Files**: `backend/app/agents/leader.py`, `backend/app/agents/orchestrator.py`

---

## Phase 1: Quality Improvements (SHOULD DO)

### P1-1: Remove forced Chinese from code-generating agents ✅ DONE (partial)
- **Issue**: `base.py:65` appends "请始终用中文回复" to ALL agent system prompts
- **Effect**: Degrades English code quality; LLMs write better HTML/CSS/JS when prompted in English
- **Fix**: Keep Chinese for PM/Leader user-facing messages; Engineer act prompt outputs 1句中文总结+代码; think step outputs中文设计文档

### P1-2: Default mode → engineer (not team) ✅ DONE
- **Issue**: `store.ts:101` defaults to "team" mode
- **Effect**: Every new project starts with heavy multi-agent flow; simple requests get over-processed
- **Fix**: Changed default to "engineer"; user selects team mode when needed

### P1-3: Fix API_BASE to use environment variables ✅ DONE
- **Issue**: `api.ts:3-4` hardcodes production URL
- **Effect**: No dev/prod flexibility; all development hits production
- **Fix**: Use `process.env.NEXT_PUBLIC_API_URL` with production URL fallback

---

## Phase 2: Polish & Innovation (NICE TO HAVE)

### P2-1: Frontend UI Polish — Align with Atoms.dev UX ✅ DONE
- Mode selector with icons (Engineer/Team/Race/Research/Review)
- Stop generation button
- Responsive viewport toggle (desktop/tablet/mobile)
- Console error display with auto-fix
- Full Chinese UI
- Guest experience button

### P2-2: SEARCH/REPLACE Diff Iteration Editing ❌ NOT DONE
- Instead of full rebuild, use Aider-style SEARCH/REPLACE blocks
- Token-efficient, faster iteration, preserves manual edits
- Requires: diff parser in backend, frontend diff viewer

### P2-3: Visual Self-Check Loop ❌ NOT DONE
- After code generation, render in headless browser
- Feed screenshot back to LLM for comparison
- Auto-fix visual issues before showing to user
- (Significant complexity — only if time allows)

---

## Additional Improvements (Done Post-Phase 2)

### Think Step — 设计文档与代码分离 ✅ DONE
- Engineer code generation now has two phases: Think (设计文档, max_tokens=2048) → Act (1句中文总结+代码, max_tokens=65536)
- Design doc streamed via agent_stream events, visible to user
- Prevents design text from being extracted as HTML (causing blank iframe)

### 截断检测+自动续写 ✅ DONE
- `is_js_truncated()` checks LAST `<script>` block (not first — first is Tailwind CDN config)
- Checks HTML ending for `</script></body></html>`
- `_continue_code()` sends truncated code to LLM for continuation, max 3 attempts
- E2E verified: all 6 large projects (up to 61K chars) complete without blank pages

### LLM Migration to DeepSeek V4 Pro ✅ DONE
- Replaced unavailable NVIDIA/Agnes with DeepSeek V4 Pro
- `deepseek-v4-pro` model, API via `https://api.deepseek.com`
- max_tokens=65536 (DeepSeek hard limit)
- From China: uses system proxy `HTTP_PROXY=http://127.0.0.1:1088`
- httpx `trust_env=True` for proxy support

### LLM 超时保护 ✅ DONE
- `LLM_TOTAL_TIMEOUT=600s` (up from 150s)
- httpx Timeout: `connect=30s, read=600s, write=30s, pool=30s`
- Heartbeat limit: `MAX_HEARTBEATS=2`
- Friendly Chinese error messages on timeout

### Agent Thinking 去重 ✅ DONE
- Same agent name only creates one thinking message in SSE stream
- Subsequent steps (think→act) append stream text to same message

### 审批流程移除 ✅ DONE
- `approval_request` event removed from orchestrator
- All steps auto-approved, reducing interaction friction

---

## Evaluation Criteria Mapping

| Interview Criteria | What We Address |
|---|---|
| 完成度 | P0 fixes + regression tests = working demo; 6 large projects E2E verified |
| 工程思维 | P0-3 iteration awareness shows task decomposition; Think Step shows process transparency; truncation fix shows defensive engineering |
| 用户体验 | P0-2 Tailwind mandate = professional UI; engineer default = faster; Chinese UI; guest access |
| 创新性 | Think Step design doc streaming; multi-agent SOP with smart skip; truncation auto-continuation |
| 可交付性 | PROJECT_PLAN.md + README.md + EXAM_DOC.md + deployed demo + GitHub |

---

## Architecture Diagram (Current)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Chat UI    │────▶│  Orchestrator │────▶│   Agents     │
│  (Next.js)   │◀────│  (FastAPI)    │◀────│  (8 roles)   │
│              │     │              │     │              │
│  - SSE stream│     │  - plan mode │     │  - PM (Emma) │
│  - @mention  │     │  - iteration │     │  - Architect │
│  - mode select│    │  - think step│     │  - Engineer  │
│  - stop btn  │     │  - truncation│     │  - Leader    │
│  - auto-fix  │     │    fix       │     │  - Reviewer  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       │             ┌──────▼──────┐       ┌──────▼──────┐
       │             │  LLM Router │       │  Code Store │
       │             │  (DeepSeek  │       │  (SQLite +  │
       │             │   V4 Pro)   │       │   versions) │
       │             └─────────────┘       └─────────────┘
       │                                           │
  ┌────▼────┐                              ┌──────▼──────┐
  │ Preview  │                              │  HTML/CSS   │
  │ (iframe) │◀─────────────────────────────│  + Tailwind │
  │ sandbox  │                              │  via CDN    │
  └─────────┘                              └─────────────┘
```

---

## Current Status
- [x] Deep research on Atoms.dev
- [x] Deep research on AI code generation SOTA (v0, bolt, lovable, aider)
- [x] Full codebase audit identifying root causes
- [x] P0 fixes (3 items)
- [x] P1 improvements (3 items)
- [x] P2-1 Polish (UI alignment with Atoms.dev)
- [x] Think Step design doc
- [x] Truncation detection + auto-continuation
- [x] LLM migration to DeepSeek V4 Pro
- [x] LLM timeout protection (600s)
- [x] Agent thinking dedup
- [x] Approval flow removal
- [x] Full Chinese UI
- [x] Guest experience
- [x] Regression testing (35+ items)
- [x] Large project E2E verification (6 projects: Mario/Dashboard/Ecommerce/Snake/Calculator/KOF)
- [x] Railway deployment (both services Online)
- [x] Documentation update (README/EXAM_DOC/PROJECT_PLAN)
- [ ] P2-2 SEARCH/REPLACE diff iteration
- [ ] P2-3 Visual self-check loop
- [ ] Final submission

---

## Key Files Reference
| File | Purpose |
|---|---|
| `backend/app/agents/orchestrator.py` | Agent coordination, team mode plan execution, Think Step, truncation fix, timeout protection |
| `backend/app/agents/engineer.py` | Code generation prompts — DESIGN_SYSTEM + act prompt + game enhancement + think prompt |
| `backend/app/agents/leader.py` | Team mode planning — iteration awareness, smart skip |
| `backend/app/agents/base.py` | Base agent class |
| `backend/app/utils/html_utils.py` | HTML extraction + JS truncation detection (`is_js_truncated`) |
| `backend/app/utils/llm.py` | LLM provider — DeepSeek V4 Pro, trust_env, 600s timeout, max_tokens=65536 |
| `backend/app/main.py` | Proxy logic — NVIDIA clear proxy, DeepSeek keep system proxy |
| `backend/app/services/chat_service.py` | Chat flow, iteration detection |
| `frontend/src/lib/store.ts` | Zustand stores, default mode=engineer |
| `frontend/src/lib/api.ts` | API client, SSE_BASE, production URL fallback |
| `frontend/src/components/chat/ChatPanel.tsx` | Chat UI, SSE handling, auto-fix, agent_thinking dedup |
| `frontend/src/components/chat/MessageBubble.tsx` | streamText 2000 char limit + whitespace-pre-wrap |
| `frontend/src/components/preview/PreviewPanel.tsx` | Preview iframe, sandbox flags fixed |
