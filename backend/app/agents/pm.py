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
            "You are a senior product manager, skilled at understanding user needs and translating them into clear, actionable product requirements. "
            "You create detailed PRDs with features, user stories, and acceptance criteria. "
            "You are empathetic, detail-oriented, and user-centric."
        )

    @property
    def avatar_emoji(self) -> str:
        return "👩‍💻"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        original_request = context.get("original_request", task)
        return (
            f"As product manager Emma, create a PRD for the following product.\n\n"
            f"ORIGINAL USER REQUEST: {original_request}\n"
            f"YOUR ASSIGNMENT: {task}\n\n"
            f"CRITICAL: The PRD MUST be for the product the user actually requested. "
            f"If the user asked for a calculator, the PRD is for a calculator — NOT a health app, NOT a dashboard, NOT anything else. "
            f"Stay strictly on-topic. Do not invent a different product.\n\n"
            f"Create a product requirements document with:\n"
            f"- title: Product name matching the user's request\n"
            f"- overview: Product overview matching the user's request\n"
            f"- features: Array of {{name, description, priority}} — features for THIS specific product\n"
            f"- user_stories: Array of user story strings\n"
            f"- acceptance_criteria: Array of acceptance criteria strings\n\n"
            f"Output in JSON format."
        )

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_think_prompt(task, context)
        if llm_provider.is_mock:
            return MOCK_RESPONSES.get("pm", "")
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


from app.utils.llm import MOCK_RESPONSES
