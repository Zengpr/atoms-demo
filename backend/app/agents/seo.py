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
        return "快速推出 SEO 页面并自动化优化，以更低的成本快速带来自然流量。"

    @property
    def avatar_emoji(self) -> str:
        return "\U0001F680"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"分析以下项目的SEO策略:\n\n需求: {task}\n\n提供关键词分析、页面结构建议和内容策略。"
        return await self._llm_generate(prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"为以下项目创建SEO优化方案:\n\n需求: {task}\n\n输出JSON格式，包含: keywords, meta_tags, page_structure, content_strategy。"
        return await self._llm_generate(prompt)

    async def _llm_generate(self, prompt: str) -> str:
        from app.utils.llm import llm_provider
        return await llm_provider.generate(self.get_system_prompt(), prompt)
