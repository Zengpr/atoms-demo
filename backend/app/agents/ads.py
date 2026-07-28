from app.agents.base import BaseAgent
from typing import Any


class AdsAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Adrian"

    @property
    def role(self) -> str:
        return "Ads Specialist"

    @property
    def description(self) -> str:
        return "Automate Google Ads operations. Manage ad campaign creation, tracking, and optimization to help you scale growth with less effort."

    @property
    def avatar_emoji(self) -> str:
        return "\U0001F4E2"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"Analyze the advertising strategy for the following project:\n\nRequirements: {task}\n\nProvide target audience analysis, ad channel recommendations, and budget allocation."
        return await self._llm_generate(prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"Create an advertising plan for the following project:\n\nRequirements: {task}\n\nOutput in JSON format with: target_audience, channels, budget_allocation, ad_copy_suggestions, kpis."
        return await self._llm_generate(prompt)

    async def _llm_generate(self, prompt: str) -> str:
        from app.utils.llm import llm_provider
        return await llm_provider.generate(self.get_system_prompt(), prompt)
