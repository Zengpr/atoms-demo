import json
from typing import Any
from app.agents.base import BaseAgent
from app.utils.llm import llm_provider


class ResearcherAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Iris"

    @property
    def role(self) -> str:
        return "Deep Researcher"

    @property
    def description(self) -> str:
        return (
            "You are a meticulous Deep Researcher who investigates topics thoroughly. "
            "You gather relevant information, identify best practices, and provide "
            "comprehensive research findings with actionable recommendations. "
            "You are thorough, evidence-based, and insightful."
        )

    @property
    def avatar_emoji(self) -> str:
        return "🔬"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        return (
            f"As Iris the Researcher, analyze this topic:\n\n"
            f"Topic: {task}\n\n"
            f"Provide research findings with:\n"
            f"- findings: Array of key findings\n"
            f"- best_practices: Array of best practices\n"
            f"- recommendations: Summary recommendations string\n\n"
            f"Output as JSON."
        )

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_think_prompt(task, context)
        if llm_provider.is_mock:
            from app.utils.llm import MOCK_RESPONSES
            return MOCK_RESPONSES.get("researcher", "")
        result = await llm_provider.generate(self.get_system_prompt(), prompt)
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            return result

    async def act(self, task: str, context: dict[str, Any]) -> str:
        thought = context.get("thought", "")
        try:
            research = json.loads(thought)
            return json.dumps(research)
        except json.JSONDecodeError:
            return thought
