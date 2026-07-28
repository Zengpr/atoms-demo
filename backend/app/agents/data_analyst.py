from app.agents.base import BaseAgent
from typing import Any


class DataAnalystAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "David"

    @property
    def role(self) -> str:
        return "Data Analyst"

    @property
    def description(self) -> str:
        return "Discover growth opportunities by analyzing massive datasets. Present clear insights to help you make smarter, data-driven decisions."

    @property
    def avatar_emoji(self) -> str:
        return "\U0001F4CA"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"Analyze the data requirements for the following project:\n\nRequirements: {task}\n\nProvide data collection strategy, analysis method recommendations, and key metric definitions."
        return await self._llm_generate(prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"Create a data analysis plan for the following project:\n\nRequirements: {task}\n\nOutput in JSON format with: metrics, data_sources, analysis_methods, visualizations, insights."
        return await self._llm_generate(prompt)

    async def _llm_generate(self, prompt: str) -> str:
        from app.utils.llm import llm_provider
        return await llm_provider.generate(self.get_system_prompt(), prompt)
