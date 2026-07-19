import json
from typing import Any
from app.agents.base import BaseAgent
from app.utils.llm import llm_provider


class PMAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Emma"

    @property
    def role(self) -> str:
        return "Product Manager"

    @property
    def description(self) -> str:
        return (
            "You are a senior Product Manager who excels at understanding user needs "
            "and translating them into clear, actionable product requirements. You create "
            "detailed PRDs with features, user stories, and acceptance criteria. "
            "You are empathetic, detail-oriented, and user-focused."
        )

    @property
    def avatar_emoji(self) -> str:
        return "👩‍💻"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = (
            f"As Emma the Product Manager, analyze this request and create a PRD:\n\n"
            f"Request: {task}\n\n"
            f"Create a Product Requirements Document with:\n"
            f"- title: PRD title\n"
            f"- overview: Brief product overview\n"
            f"- features: Array of {{name, description, priority}}\n"
            f"- user_stories: Array of user story strings\n"
            f"- acceptance_criteria: Array of criteria strings\n\n"
            f"Output as JSON."
        )
        result = await llm_provider.generate(self.get_system_prompt(), prompt)
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            return result

    async def act(self, task: str, context: dict[str, Any]) -> str:
        thought = context.get("thought", "")
        try:
            prd = json.loads(thought)
            return json.dumps(prd)
        except json.JSONDecodeError:
            return thought
