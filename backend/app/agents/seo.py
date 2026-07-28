from app.agents.base import BaseAgent
from typing import Any


class SEOAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Sarah"

    @property
    def role(self) -> str:
        return "SEO Specialist"

    @property
    def description(self) -> str:
        return "Rapidly launch SEO pages and automate optimization to drive organic traffic faster at lower cost."

    @property
    def avatar_emoji(self) -> str:
        return "\U0001F680"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"Analyze the SEO strategy for the following project:\n\nRequirements: {task}\n\nProvide keyword analysis, page structure recommendations, and content strategy."
        return await self._llm_generate(prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"Create an SEO optimization plan for the following project:\n\nRequirements: {task}\n\nOutput in JSON format with: keywords, meta_tags, page_structure, content_strategy."
        return await self._llm_generate(prompt)

    async def _llm_generate(self, prompt: str) -> str:
        from app.utils.llm import llm_provider
        return await llm_provider.generate(self.get_system_prompt(), prompt)
