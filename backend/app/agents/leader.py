import json
from typing import Any
from app.agents.base import BaseAgent
from app.utils.llm import llm_provider


class LeaderAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Mike"

    @property
    def role(self) -> str:
        return "Team Leader & Coordinator"

    @property
    def description(self) -> str:
        return (
            "You are the team leader, responsible for coordinating the entire development process. "
            "You analyze user requirements, break them into tasks, and assign them to the right team members. "
            "You ensure the quality and consistency of all deliverables. You are decisive, organized, and communicative."
        )

    @property
    def avatar_emoji(self) -> str:
        return "👨‍💼"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        is_iteration = context.get("is_iteration", False)
        previous_code = context.get("previous_code", "")
        mode = context.get("mode", "team")

        prompt = (
            f"As team leader Mike, analyze this request and create an execution plan:\n\n"
            f"User request: {task}\n\n"
            f"Project mode: {mode}\n\n"
        )

        if is_iteration and previous_code:
            prompt += (
                "IMPORTANT CONTEXT: This is an ITERATION request — the user wants to modify an existing application.\n"
                "The application already exists and is working. The user just wants specific changes.\n\n"
                "DECISION RULES for iteration requests:\n"
                "- For simple changes (color, text, layout tweaks, adding a button, fixing a bug): "
                "assign ONLY key='engineer' (Alex). Skip PM and Architect.\n"
                "- For moderate changes (adding a new feature, significant UI overhaul): "
                "assign key='architect' then key='engineer'. Skip PM.\n"
                "- Only for major re-scoping (completely different app, new major module): "
                "use the full pipeline: key='pm' → key='architect' → key='engineer'.\n\n"
                "When in doubt, use FEWER steps. Iteration should be fast, not a full planning cycle.\n\n"
            )
        else:
            prompt += (
                "This is a NEW project request. Plan the appropriate agent pipeline:\n"
                "- Simple apps (counter, calculator, landing page): key='engineer' only\n"
                "- Standard apps (dashboard, todo, form): key='architect' → key='engineer'\n"
                "- Complex apps (full-stack, multi-feature): key='pm' → key='architect' → key='engineer'\n\n"
            )

        prompt += (
            "Available agents (use EXACT key as the 'agent' value):\n"
            "- key='pm' (Emma): Requirements analysis, PRD generation\n"
            "- key='architect' (Bob): System design, tech selection\n"
            "- key='engineer' (Alex): Code implementation\n"
            "- key='researcher' (Iris): In-depth research\n\n"
            "Output a JSON plan with 'plan' (summary), 'steps' (array of {agent, task}), "
            "and 'summary' (one-sentence summary). "
            "CRITICAL: The 'agent' field MUST be the key string (pm, architect, engineer, researcher), NOT the name."
        )
        return prompt

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_think_prompt(task, context)
        is_iteration = context.get("is_iteration", False)
        if llm_provider.is_mock:
            if is_iteration:
                return json.dumps({
                    "plan": "Quick iteration — assign engineer directly.",
                    "steps": [
                        {"agent": "engineer", "task": f"Modify existing app: {task}"}
                    ],
                    "summary": "Engineer-only iteration"
                })
            return json.dumps({
                "plan": "I'll coordinate the team to build this application step by step.",
                "steps": [
                    {"agent": "pm", "task": f"Analyze requirements for: {task}"},
                    {"agent": "architect", "task": f"Design architecture for: {task}"},
                    {"agent": "engineer", "task": f"Implement: {task}"}
                ],
                "summary": "Full team pipeline: PM → Architect → Engineer"
            })
        result = await llm_provider.generate(self.get_system_prompt(), prompt)
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            if is_iteration:
                return json.dumps({
                    "plan": "Quick iteration — assign engineer directly.",
                    "steps": [
                        {"agent": "engineer", "task": f"Modify existing app: {task}"}
                    ],
                    "summary": "Engineer-only iteration"
                })
            return json.dumps({
                "plan": "I'll coordinate the team to build this application step by step.",
                "steps": [
                    {"agent": "pm", "task": f"Analyze requirements for: {task}"},
                    {"agent": "architect", "task": f"Design architecture for: {task}"},
                    {"agent": "engineer", "task": f"Implement: {task}"}
                ],
                "summary": "Full team pipeline: PM → Architect → Engineer"
            })

    async def act(self, task: str, context: dict[str, Any]) -> str:
        thought = context.get("thought", "")
        try:
            plan_data = json.loads(thought)
            return json.dumps(plan_data)
        except json.JSONDecodeError:
            return thought
