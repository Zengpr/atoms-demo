# Atoms Demo — Project Improvement Plan

## Context
- **Goal**: Build a polished, production-quality AI Agent code generation platform demo for 深度赋智 (ROOT) full-stack engineer interview
- **Reference**: Atoms.dev (8 specialized agents, SOP collaboration, visual editor, Atoms Cloud)
- **Deadline**: ASAP — 48h from task receipt
- **Stakes**: 40k×15 salary position

---

## Phase 0: Critical Bug Fixes (MUST DO FIRST)

### P0-1: Fix html_utils.py — Don't return raw text as HTML
- **Root Cause**: `extract_html()` at line 26-28 treats ANY text containing `<div>` or `<body>` as HTML
- **Effect**: When LLM outputs analysis text before code (e.g., "1. **Analysis** — <div> structure..."), the ENTIRE response including analysis is rendered as broken HTML → "layout disorder"
- **Fix**: Only extract content between `<!DOCTYPE html>` or `<html>` tags; strip anything before the HTML start tag
- **File**: `backend/app/utils/html_utils.py:26-28`

### P0-2: Rewrite Engineer Agent Prompt
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

### P0-3: Fix Team Mode Iteration Awareness
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

### P1-1: Remove forced Chinese from code-generating agents
- **Issue**: `base.py:65` appends "请始终用中文回复" to ALL agent system prompts
- **Effect**: Degrades English code quality; LLMs write better HTML/CSS/JS when prompted in English
- **Fix**: Keep Chinese for PM/Leader user-facing messages; remove from Engineer act prompt (already partially done)

### P1-2: Default mode → engineer (not team)
- **Issue**: `store.ts:101` defaults to "team" mode
- **Effect**: Every new project starts with heavy multi-agent flow; simple requests get over-processed
- **Fix**: Change default to "engineer"; user selects team mode when needed

### P1-3: Fix API_BASE to use environment variables
- **Issue**: `api.ts:3-4` hardcodes production URL
- **Effect**: No dev/prod flexibility; all development hits production
- **Fix**: Use `process.env.NEXT_PUBLIC_API_URL` with localhost fallback

---

## Phase 2: Polish & Innovation (NICE TO HAVE)

### P2-1: Frontend UI Polish — Align with Atoms.dev UX
- Mode selector with icons (Engineer/Team/Race/Research)
- Agent @mention support in chat input
- Stop generation button
- Responsive viewport toggle (desktop/tablet/mobile)
- Console error display with "Resolve" button

### P2-2: SEARCH/REPLACE Diff Iteration Editing
- Instead of full rebuild, use Aider-style SEARCH/REPLACE blocks
- Token-efficient, faster iteration, preserves manual edits
- Requires: diff parser in backend, frontend diff viewer

### P2-3: Visual Self-Check Loop
- After code generation, render in headless browser
- Feed screenshot back to LLM for comparison
- Auto-fix visual issues before showing to user
- (Significant complexity — only if time allows)

---

## Evaluation Criteria Mapping

| Interview Criteria | What We Address |
|---|---|
| 完成度 | P0 fixes + regression tests = working demo |
| 工程思维 | P0-3 iteration awareness shows task decomposition; P2-2 diff editing shows complexity control |
| 用户体验 | P0-2 Tailwind mandate = professional UI; P1-2 engineer default = faster interaction |
| 创新性 | Multi-agent SOP (team mode); Race mode (if implemented); Visual self-check (P2-3) |
| 可交付性 | PROJECT_PLAN.md + clear documentation + deployed demo + GitHub |

---

## Architecture Diagram (Target)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Chat UI    │────▶│  Orchestrator │────▶│   Agents     │
│  (Next.js)   │◀────│  (FastAPI)    │◀────│  (8 roles)   │
│              │     │              │     │              │
│  - SSE stream│     │  - plan mode │     │  - PM (Emma) │
│  - @mention  │     │  - iteration │     │  - Architect │
│  - mode select│    │  - context   │     │  - Engineer  │
│  - stop btn  │     │    mgmt      │     │  - Leader    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       │             ┌──────▼──────┐       ┌──────▼──────┐
       │             │  LLM Router │       │  Code Store │
       │             │  (multi-    │       │  (SQLite +  │
       │             │   model)    │       │   versions) │
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
- [ ] P0 fixes (3 items)
- [ ] P1 improvements (3 items)
- [ ] P2 polish (optional)
- [ ] Regression testing (5 items from reviewer)
- [ ] Deploy + submit

---

## Key Files Reference
| File | Purpose |
|---|---|
| `backend/app/agents/orchestrator.py` | Agent coordination, team mode plan execution |
| `backend/app/agents/engineer.py` | Code generation prompts — MAIN QUALITY DRIVER |
| `backend/app/agents/leader.py` | Team mode planning — needs iteration awareness |
| `backend/app/agents/base.py` | Base agent class — has forced Chinese issue |
| `backend/app/utils/html_utils.py` | HTML extraction — CRITICAL BUG |
| `backend/app/services/chat_service.py` | Chat flow, iteration detection |
| `frontend/src/store.ts` | Zustand stores, default mode |
| `frontend/src/lib/api.ts` | API client, hardcoded URLs |
| `frontend/src/components/chat/ChatPanel.tsx` | Chat UI, SSE handling |
| `frontend/src/components/preview/PreviewPanel.tsx` | Preview iframe |
