import json
import re
import asyncio
import time
from typing import Any, AsyncIterator
from app.agents.base import BaseAgent
from app.agents.leader import LeaderAgent
from app.agents.pm import PMAgent
from app.agents.architect import ArchitectAgent
from app.agents.engineer import EngineerAgent
from app.agents.researcher import ResearcherAgent
from app.utils.llm import llm_provider


MOCK_DELAY = 0.5


async def _mock_delay():
    if llm_provider.is_mock:
        await asyncio.sleep(MOCK_DELAY)


async def _stream_llm_as_events(
    agent: BaseAgent,
    stream_method: str,
    task: str,
    context: dict[str, Any],
) -> AsyncIterator[dict[str, Any]]:
    method = getattr(agent, stream_method)
    full_text = ""
    async for chunk in method(task, context):
        full_text += chunk
        yield {
            "event": "agent_stream",
            "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "chunk": chunk},
        }
    yield {
        "event": "agent_stream_done",
        "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "full_text": full_text},
    }


async def _collect_stream(stream: AsyncIterator[dict[str, Any]]) -> str:
    full = ""
    async for ev in stream:
        if ev["event"] == "agent_stream_done":
            full = ev["data"]["full_text"]
    return full


class Orchestrator:
    def __init__(self):
        self.agents: dict[str, BaseAgent] = {
            "leader": LeaderAgent(),
            "pm": PMAgent(),
            "architect": ArchitectAgent(),
            "engineer": EngineerAgent(),
            "researcher": ResearcherAgent(),
        }

    def get_agent(self, name: str) -> BaseAgent | None:
        return self.agents.get(name)

    async def run_engineer_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        engineer = self.agents["engineer"]
        start = time.time()

        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"{engineer.avatar_emoji} {engineer.name} is analyzing your request..."},
        }

        think_gen = _stream_llm_as_events(engineer, "think_stream", task, context)
        thought = ""
        async for ev in think_gen:
            if ev["event"] == "agent_stream":
                yield ev
            elif ev["event"] == "agent_stream_done":
                thought = ev["data"]["full_text"]

        await _mock_delay()

        yield {
            "event": "agent_action",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "action": "Implementing your application based on the analysis..."},
        }

        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"{engineer.avatar_emoji} {engineer.name} is writing code..."},
        }

        act_context = {**context, "thought": thought}
        code = ""
        act_gen = _stream_llm_as_events(engineer, "act_stream", task, act_context)
        async for ev in act_gen:
            if ev["event"] == "agent_stream":
                code += ev["data"]["chunk"]
                yield ev
            elif ev["event"] == "agent_stream_done":
                code = ev["data"]["full_text"]

        code = self._extract_html(code)
        duration = int((time.time() - start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code, "duration_ms": duration},
        }

        yield {
            "event": "message_complete",
            "data": {
                "agent": engineer.name,
                "message": "Application generated! Preview it on the right, or tell me what you'd like to change — I can iterate on the design, layout, colors, or add new features.",
                "duration_ms": duration,
            },
        }

    async def run_team_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        leader = self.agents["leader"]
        pm = self.agents["pm"]
        architect = self.agents["architect"]
        engineer = self.agents["engineer"]

        enriched_context = dict(context)
        enriched_context["mode"] = "team"
        total_start = time.time()

        yield {
            "event": "agent_thinking",
            "data": {"agent": leader.name, "emoji": leader.avatar_emoji, "message": f"{leader.avatar_emoji} {leader.name} is coordinating the team..."},
        }

        leader_text = ""
        async for ev in _stream_llm_as_events(leader, "think_stream", task, enriched_context):
            if ev["event"] == "agent_stream":
                leader_text = ev["data"]["chunk"] if not leader_text else leader_text
                yield ev
            elif ev["event"] == "agent_stream_done":
                leader_text = ev["data"]["full_text"]

        try:
            plan_data = json.loads(leader_text)
        except json.JSONDecodeError:
            plan_data = {"plan": leader_text[:200], "steps": [], "summary": "Executing full team pipeline"}

        plan_summary = plan_data.get("plan", leader_text[:200])
        yield {
            "event": "agent_action",
            "data": {
                "agent": leader.name,
                "emoji": leader.avatar_emoji,
                "action": f"Team plan: {plan_summary}",
                "plan": plan_data,
            },
        }

        await _mock_delay()

        yield {
            "event": "agent_thinking",
            "data": {"agent": pm.name, "emoji": pm.avatar_emoji, "message": f"{pm.avatar_emoji} {pm.name} is analyzing requirements..."},
        }

        prd_text = ""
        async for ev in _stream_llm_as_events(pm, "think_stream", task, enriched_context):
            if ev["event"] == "agent_stream":
                yield ev
            elif ev["event"] == "agent_stream_done":
                prd_text = ev["data"]["full_text"]

        try:
            prd_data = json.loads(prd_text)
        except json.JSONDecodeError:
            prd_data = {"prd": {"title": "Product Requirements", "overview": prd_text[:200]}}

        enriched_context["prd"] = prd_text
        prd_overview = prd_data.get("prd", {}).get("overview", prd_text[:200])
        features = prd_data.get("prd", {}).get("features", [])
        feature_names = ", ".join(f.get("name", "") for f in features[:3]) if features else ""

        yield {
            "event": "agent_action",
            "data": {
                "agent": pm.name,
                "emoji": pm.avatar_emoji,
                "action": f"PRD created — {feature_names}" if feature_names else "PRD created",
                "prd": prd_data,
            },
        }

        await _mock_delay()

        yield {
            "event": "agent_thinking",
            "data": {"agent": architect.name, "emoji": architect.avatar_emoji, "message": f"{architect.avatar_emoji} {architect.name} is designing the architecture..."},
        }

        arch_text = ""
        async for ev in _stream_llm_as_events(architect, "think_stream", task, enriched_context):
            if ev["event"] == "agent_stream":
                yield ev
            elif ev["event"] == "agent_stream_done":
                arch_text = ev["data"]["full_text"]

        try:
            arch_data = json.loads(arch_text)
        except json.JSONDecodeError:
            arch_data = {"architecture": {"tech_stack": {"frontend": "HTML5 + CSS3 + JS"}, "component_structure": []}}

        enriched_context["architecture"] = arch_text

        yield {
            "event": "agent_action",
            "data": {
                "agent": architect.name,
                "emoji": architect.avatar_emoji,
                "action": "Architecture designed",
                "architecture": arch_data,
            },
        }

        await _mock_delay()

        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"{engineer.avatar_emoji} {engineer.name} is building your application..."},
        }

        code = ""
        act_gen = _stream_llm_as_events(engineer, "act_stream", task, enriched_context)
        async for ev in act_gen:
            if ev["event"] == "agent_stream":
                code += ev["data"]["chunk"]
                yield ev
            elif ev["event"] == "agent_stream_done":
                code = ev["data"]["full_text"]

        code = self._extract_html(code)
        total_duration = int((time.time() - total_start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code, "duration_ms": total_duration},
        }

        yield {
            "event": "message_complete",
            "data": {
                "agent": leader.name,
                "message": f"Team complete! {pm.name} wrote the PRD, {architect.name} designed the architecture, and {engineer.name} built the app. Preview it on the right — or tell me what to adjust and I'll coordinate the team to iterate.",
                "duration_ms": total_duration,
                "agents_used": [leader.name, pm.name, architect.name, engineer.name],
            },
        }

    async def run_race_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        engineer = self.agents["engineer"]

        yield {
            "event": "agent_thinking",
            "data": {"agent": "Race Mode", "emoji": "⚡", "message": "⚡ Race Mode: Launching two parallel implementation strategies..."},
        }

        start = time.time()

        code_a = ""
        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"Strategy A: {engineer.avatar_emoji} {engineer.name} is building..."},
        }
        act_gen_a = _stream_llm_as_events(engineer, "act_stream", task, context)
        async for ev in act_gen_a:
            if ev["event"] == "agent_stream":
                code_a += ev["data"]["chunk"]
                yield ev
            elif ev["event"] == "agent_stream_done":
                code_a = ev["data"]["full_text"]

        code_a = self._extract_html(code_a)

        context_b = {**context}
        code_b = ""
        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"Strategy B: {engineer.avatar_emoji} {engineer.name} is building alternative..."},
        }
        act_gen_b = _stream_llm_as_events(engineer, "act_stream", f"Alternative creative approach: {task}", context_b)
        async for ev in act_gen_b:
            if ev["event"] == "agent_stream":
                code_b += ev["data"]["chunk"]
                yield ev
            elif ev["event"] == "agent_stream_done":
                code_b = ev["data"]["full_text"]

        code_b = self._extract_html(code_b)
        duration = int((time.time() - start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code_a, "variant": "A", "duration_ms": duration},
        }
        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code_b, "variant": "B", "duration_ms": duration},
        }

        yield {
            "event": "message_complete",
            "data": {
                "agent": "Race Mode",
                "message": f"Race complete! Two variants generated in {duration}ms. Preview both and tell me which direction you prefer.",
                "duration_ms": duration,
                "variants": ["A", "B"],
            },
        }

    async def run_research_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        researcher = self.agents["researcher"]
        start = time.time()

        yield {
            "event": "agent_thinking",
            "data": {"agent": researcher.name, "emoji": researcher.avatar_emoji, "message": f"{researcher.avatar_emoji} {researcher.name} is conducting deep research..."},
        }

        research_text = ""
        async for ev in _stream_llm_as_events(researcher, "think_stream", task, context):
            if ev["event"] == "agent_stream":
                yield ev
            elif ev["event"] == "agent_stream_done":
                research_text = ev["data"]["full_text"]

        duration = int((time.time() - start) * 1000)

        yield {
            "event": "message_complete",
            "data": {
                "agent": researcher.name,
                "message": "Research complete! Ask follow-up questions or switch to Engineer/Team mode to build based on these findings.",
                "duration_ms": duration,
            },
        }

    async def run_review_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        researcher = self.agents["researcher"]
        engineer = self.agents["engineer"]
        start = time.time()

        previous_code = context.get("previous_code", "")
        review_task = f"Review this code and suggest improvements:\n\n{previous_code[:3000]}\n\nUser request: {task}" if previous_code else task

        yield {
            "event": "agent_thinking",
            "data": {"agent": researcher.name, "emoji": researcher.avatar_emoji, "message": f"{researcher.avatar_emoji} {researcher.name} is reviewing the code..."},
        }

        thought = ""
        async for ev in _stream_llm_as_events(researcher, "think_stream", review_task, context):
            if ev["event"] == "agent_stream":
                yield ev
            elif ev["event"] == "agent_stream_done":
                thought = ev["data"]["full_text"]

        yield {
            "event": "agent_action",
            "data": {"agent": researcher.name, "emoji": researcher.avatar_emoji, "action": "Review complete. Applying improvements..."},
        }

        await _mock_delay()

        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"{engineer.avatar_emoji} {engineer.name} is applying review feedback..."},
        }

        act_context = {**context, "thought": thought, "is_iteration": True}
        code = ""
        act_gen = _stream_llm_as_events(engineer, "act_stream", task, act_context)
        async for ev in act_gen:
            if ev["event"] == "agent_stream":
                code += ev["data"]["chunk"]
                yield ev
            elif ev["event"] == "agent_stream_done":
                code = ev["data"]["full_text"]

        code = self._extract_html(code)
        duration = int((time.time() - start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code, "duration_ms": duration},
        }

        yield {
            "event": "message_complete",
            "data": {
                "agent": researcher.name,
                "message": "Review complete! I've analyzed the code and applied improvements. Check the preview or ask for further refinements.",
                "duration_ms": duration,
                "agents_used": [researcher.name, engineer.name],
            },
        }

    async def run(self, task: str, mode: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        if mode == "engineer":
            async for event in self.run_engineer_mode(task, context):
                yield event
        elif mode == "race":
            async for event in self.run_race_mode(task, context):
                yield event
        elif mode in ("research", "review"):
            if mode == "review":
                async for event in self.run_review_mode(task, context):
                    yield event
            else:
                async for event in self.run_research_mode(task, context):
                    yield event
        else:
            async for event in self.run_team_mode(task, context):
                yield event

    @staticmethod
    def _extract_html(text: str) -> str:
        fence_match = re.search(r"```html\s*\n(.*?)```", text, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()
        fence_match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
        if fence_match:
            content = fence_match.group(1).strip()
            if content.lower().startswith("<!doctype") or content.lower().startswith("<html"):
                return content
        if text.strip().lower().startswith("<!doctype") or text.strip().lower().startswith("<html"):
            return text.strip()
        html_start = text.find("<!DOCTYPE")
        if html_start == -1:
            html_start = text.find("<html")
        if html_start != -1:
            return text[html_start:].strip()
        return text.strip()
