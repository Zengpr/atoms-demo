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
                "- For simple changes (color, text, layout tweaks, adding a button, fixing a bug, fixing console errors): "
                "assign ONLY key='engineer' (Alex). Skip PM and Architect.\n"
                "- For moderate changes (adding a new feature, significant UI overhaul): "
                "assign key='architect' then key='engineer'. Skip PM.\n"
                "- Only for major re-scoping (completely different app, new major module): "
                "use the full pipeline: key='pm' → key='architect' → key='engineer'.\n\n"
                "When in doubt, use FEWER steps. Iteration should be fast, not a full planning cycle.\n\n"
            )
        else:
            prompt += (
                "This is a NEW project request. Decide the appropriate agent pipeline based on COMPLEXITY:\n\n"
                "SIMPLE apps (calculator, counter, timer, stopwatch, to-do list, landing page, form, quiz, "
                "converter, clock, weather widget, note pad, BMI calculator, tip calculator, simple game): "
                "assign ONLY key='engineer' (Alex). Do NOT involve PM or Architect.\n\n"
                "STANDARD apps (dashboard, admin panel, e-commerce, chat app, kanban board, blog, portfolio): "
                "assign key='architect' → key='engineer'. Skip PM.\n\n"
                "COMPLEX apps (full-stack SaaS, multi-role platform, complex workflow system): "
                "use the full pipeline: key='pm' → key='architect' → key='engineer'.\n\n"
                "IMPORTANT: When in doubt, default to FEWER agents. A calculator does NOT need a PM. "
                "A to-do app does NOT need an architect. Keep it lean.\n\n"
            )

        prompt += (
            "Available agents (use EXACT key as the 'agent' value):\n"
            "- key='pm' (Emma): Requirements analysis, PRD generation\n"
            "- key='architect' (Bob): System design, tech selection\n"
            "- key='engineer' (Alex): Code implementation\n"
            "- key='researcher' (Iris): In-depth research\n\n"
            "Output a JSON plan with 'plan' (summary), 'steps' (array of {agent, task}), "
            "and 'summary' (one-sentence summary). "
            "CRITICAL: The 'agent' field MUST be the key string (pm, architect, engineer, researcher), NOT the name. "
            "CRITICAL: Each step's 'task' MUST include the ORIGINAL USER REQUEST so agents know exactly what to build. "
            "Format: \"ORIGINAL REQUEST: <user's exact words> \\n YOUR TASK: <specific assignment>\""
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
                        {"agent": "engineer", "task": f"ORIGINAL REQUEST: {task}\nYOUR TASK: Modify existing app as requested"}
                    ],
                    "summary": "Engineer-only iteration"
                })
            return json.dumps({
                "plan": "Build the requested application.",
                "steps": [
                    {"agent": "engineer", "task": f"ORIGINAL REQUEST: {task}\nYOUR TASK: Build a complete, working web application"}
                ],
                "summary": "Engineer-only build"
            })
        result = await llm_provider.generate(self.get_system_prompt(), prompt)
        try:
            plan = json.loads(result)
            if not plan.get("steps"):
                plan["steps"] = [{"agent": "engineer", "task": f"ORIGINAL REQUEST: {task}\nYOUR TASK: Implement the requested application"}]
            return json.dumps(plan)
        except json.JSONDecodeError:
            if is_iteration:
                return json.dumps({
                    "plan": "Quick iteration — assign engineer directly.",
                    "steps": [
                        {"agent": "engineer", "task": f"ORIGINAL REQUEST: {task}\nYOUR TASK: Modify existing app as requested"}
                    ],
                    "summary": "Engineer-only iteration"
                })
            return json.dumps({
                "plan": "Build the requested application.",
                "steps": [
                    {"agent": "engineer", "task": f"ORIGINAL REQUEST: {task}\nYOUR TASK: Build a complete, working web application"}
                ],
                "summary": "Engineer-only build"
            })

    async def act(self, task: str, context: dict[str, Any]) -> str:
        thought = context.get("thought", "")
        try:
            plan_data = json.loads(thought)
            return json.dumps(plan_data)
        except json.JSONDecodeError:
            return thought
