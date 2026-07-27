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
        return "自动运行 Google Ads。负责管理广告系列创建、跟踪和优化，让你以更少的投入实现增长扩展。"

    @property
    def avatar_emoji(self) -> str:
        return "\U0001F4E2"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"分析以下项目的广告策略:\n\n需求: {task}\n\n提供目标受众分析、广告渠道建议和预算分配。"
        return await self._llm_generate(prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"为以下项目创建广告方案:\n\n需求: {task}\n\n输出JSON格式，包含: target_audience, channels, budget_allocation, ad_copy_suggestions, kpis。"
        return await self._llm_generate(prompt)

    async def _llm_generate(self, prompt: str) -> str:
        from app.utils.llm import llm_provider
        return await llm_provider.generate(self.get_system_prompt(), prompt)
