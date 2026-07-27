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
        return "通过分析海量数据发现增长机会。并呈现清晰洞察，帮助你做出更明智、数据驱动的决策。"

    @property
    def avatar_emoji(self) -> str:
        return "\U0001F4CA"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"分析以下项目的数据需求:\n\n需求: {task}\n\n提供数据收集策略、分析方法建议和关键指标定义。"
        return await self._llm_generate(prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = f"为以下项目创建数据分析方案:\n\n需求: {task}\n\n输出JSON格式，包含: metrics, data_sources, analysis_methods, visualizations, insights。"
        return await self._llm_generate(prompt)

    async def _llm_generate(self, prompt: str) -> str:
        from app.utils.llm import llm_provider
        return await llm_provider.generate(self.get_system_prompt(), prompt)
