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
            "You are the team leader who coordinates the entire development process. "
            "You analyze user requirements, break them down into tasks, and assign them "
            "to the appropriate team members. You ensure quality and coherence across all "
            "deliverables. You are decisive, organized, and communicative."
        )

    @property
    def avatar_emoji(self) -> str:
        return "👨‍💼"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = (
            f"As Mike the Team Leader, analyze this request and create an execution plan:\n\n"
            f"User Request: {task}\n\n"
            f"Project Mode: {context.get('mode', 'team')}\n\n"
            f"Available Agents:\n"
            f"- Emma (Product Manager): Requirements analysis, PRD generation\n"
            f"- Bob (Architect): System design, tech stack selection\n"
            f"- Alex (Engineer): Code implementation\n"
            f"- Iris (Researcher): Deep research on topics\n\n"
            f"Decide which agents to involve and in what order. "
            f"Output a JSON plan with 'plan' (summary), 'steps' (array of {{agent, task}}), "
            f"and 'summary' (one-liner)."
        )
        result = await llm_provider.generate(self.get_system_prompt(), prompt)
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
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
