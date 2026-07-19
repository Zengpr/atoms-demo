import json
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


MOCK_DELAY = 0.8


async def _mock_delay():
    if llm_provider.is_mock:
        await asyncio.sleep(MOCK_DELAY)


async def _stream_text(agent_name: str, emoji: str, text: str, chunk_size: int = 8) -> AsyncIterator[dict[str, Any]]:
    words = text.split(" ")
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        yield {
            "event": "agent_stream",
            "data": {"agent": agent_name, "emoji": emoji, "chunk": chunk + " "},
        }
        if llm_provider.is_mock:
            await asyncio.sleep(0.12)


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

        thought = await engineer.think(task, context)

        async for ev in _stream_text(engineer.name, engineer.avatar_emoji, thought):
            yield ev

        await _mock_delay()

        yield {
            "event": "agent_action",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "action": "Implementing your application based on the analysis..."},
        }

        code = await engineer.act(task, {**context, "thought": thought})
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

        # Step 1: Leader plans
        yield {
            "event": "agent_thinking",
            "data": {"agent": leader.name, "emoji": leader.avatar_emoji, "message": f"{leader.avatar_emoji} {leader.name} is coordinating the team..."},
        }

        leader_thought, plan_str = await leader.execute(task, enriched_context)
        plan_duration = int((time.time() - total_start) * 1000)

        try:
            plan_data = json.loads(plan_str)
        except json.JSONDecodeError:
            plan_data = {"plan": leader_thought, "steps": [], "summary": "Executing full team pipeline"}

        plan_summary = plan_data.get("plan", leader_thought[:200])
        async for ev in _stream_text(leader.name, leader.avatar_emoji, f"Plan: {plan_summary}"):
            yield ev

        yield {
            "event": "agent_action",
            "data": {
                "agent": leader.name,
                "emoji": leader.avatar_emoji,
                "action": f"Team plan: {plan_summary}",
                "plan": plan_data,
                "duration_ms": plan_duration,
            },
        }

        await _mock_delay()

        # Step 2: PM creates PRD
        prd_start = time.time()
        yield {
            "event": "agent_thinking",
            "data": {"agent": pm.name, "emoji": pm.avatar_emoji, "message": f"{pm.avatar_emoji} {pm.name} is analyzing requirements..."},
        }

        pm_thought, prd_str = await pm.execute(task, enriched_context)
        prd_duration = int((time.time() - prd_start) * 1000)

        try:
            prd_data = json.loads(prd_str)
        except json.JSONDecodeError:
            prd_data = {"prd": {"title": "Product Requirements", "overview": pm_thought[:200]}}

        enriched_context["prd"] = prd_str

        prd_overview = prd_data.get("prd", {}).get("overview", pm_thought[:200])
        features = prd_data.get("prd", {}).get("features", [])
        feature_names = ", ".join(f.get("name", "") for f in features[:3]) if features else ""
        prd_summary = f"PRD: {prd_overview}"
        if feature_names:
            prd_summary += f" Key features: {feature_names}."
        async for ev in _stream_text(pm.name, pm.avatar_emoji, prd_summary):
            yield ev

        yield {
            "event": "agent_action",
            "data": {
                "agent": pm.name,
                "emoji": pm.avatar_emoji,
                "action": f"PRD created — {feature_names}" if feature_names else "PRD created",
                "prd": prd_data,
                "duration_ms": prd_duration,
            },
        }

        await _mock_delay()

        # Step 3: Architect designs
        arch_start = time.time()
        yield {
            "event": "agent_thinking",
            "data": {"agent": architect.name, "emoji": architect.avatar_emoji, "message": f"{architect.avatar_emoji} {architect.name} is designing the architecture..."},
        }

        arch_thought, arch_str = await architect.execute(task, enriched_context)
        arch_duration = int((time.time() - arch_start) * 1000)

        try:
            arch_data = json.loads(arch_str)
        except json.JSONDecodeError:
            arch_data = {"architecture": {"tech_stack": {"frontend": "HTML5 + CSS3 + JS"}, "component_structure": []}}

        enriched_context["architecture"] = arch_str

        tech = arch_data.get("architecture", {}).get("tech_stack", {})
        components = arch_data.get("architecture", {}).get("component_structure", [])
        tech_summary = ", ".join(str(v) for v in tech.values()) if tech else "HTML5 + CSS3 + JS"
        comp_names = ", ".join(c.get("name", "") for c in components[:4]) if components else ""
        arch_summary = f"Architecture: Tech stack — {tech_summary}."
        if comp_names:
            arch_summary += f" Components — {comp_names}."
        async for ev in _stream_text(architect.name, architect.avatar_emoji, arch_summary):
            yield ev

        yield {
            "event": "agent_action",
            "data": {
                "agent": architect.name,
                "emoji": architect.avatar_emoji,
                "action": f"Architecture designed — {comp_names}" if comp_names else "Architecture designed",
                "architecture": arch_data,
                "duration_ms": arch_duration,
            },
        }

        await _mock_delay()

        # Step 4: Engineer implements
        eng_start = time.time()
        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"{engineer.avatar_emoji} {engineer.name} is building your application..."},
        }

        async for ev in _stream_text(engineer.name, engineer.avatar_emoji, "Writing HTML structure, applying CSS styles, implementing JavaScript interactions..."):
            yield ev

        eng_thought, code = await engineer.execute(task, enriched_context)
        eng_duration = int((time.time() - eng_start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code, "duration_ms": eng_duration},
        }

        total_duration = int((time.time() - total_start) * 1000)

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

        async for ev in _stream_text("Race Mode", "⚡", "Strategy A: Standard approach. Strategy B: Creative alternative. Both running in parallel..."):
            yield ev

        import asyncio
        start = time.time()

        async def run_variant(variant_label: str, prompt_prefix: str) -> tuple[str, str]:
            modified_task = f"{prompt_prefix}{task}"
            thought = await engineer.think(modified_task, context)
            code = await engineer.act(modified_task, {**context, "thought": thought})
            return variant_label, code

        results = await asyncio.gather(
            run_variant("A", ""),
            run_variant("B", "Alternative creative approach: "),
        )

        duration = int((time.time() - start) * 1000)

        for variant_label, code in results:
            yield {
                "event": "code_generated",
                "data": {
                    "agent": engineer.name,
                    "code": code,
                    "variant": variant_label,
                    "duration_ms": duration,
                },
            }

        yield {
            "event": "message_complete",
            "data": {
                "agent": "Race Mode",
                "message": f"Race complete! Two variants generated in {duration}ms. Preview both and tell me which direction you prefer — I can refine either one.",
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

        thought = await researcher.think(task, context)

        async for ev in _stream_text(researcher.name, researcher.avatar_emoji, thought):
            yield ev

        await _mock_delay()

        yield {
            "event": "agent_action",
            "data": {"agent": researcher.name, "emoji": researcher.avatar_emoji, "action": "Compiling research findings and recommendations..."},
        }

        findings = await researcher.act(task, {**context, "thought": thought})
        duration = int((time.time() - start) * 1000)

        async for ev in _stream_text(researcher.name, researcher.avatar_emoji, findings if isinstance(findings, str) else str(findings)):
            yield ev

        yield {
            "event": "message_complete",
            "data": {
                "agent": researcher.name,
                "message": "Research complete! Ask follow-up questions or switch to Engineer/Team mode to build based on these findings.",
                "duration_ms": duration,
            },
        }

    async def run(self, task: str, mode: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        if mode == "engineer":
            async for event in self.run_engineer_mode(task, context):
                yield event
        elif mode == "race":
            async for event in self.run_race_mode(task, context):
                yield event
        elif mode == "research":
            async for event in self.run_research_mode(task, context):
                yield event
        else:
            async for event in self.run_team_mode(task, context):
                yield event
