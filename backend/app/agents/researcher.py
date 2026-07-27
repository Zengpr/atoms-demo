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
        return "深度研究员"

    @property
    def description(self) -> str:
        return (
            "你是严谨的深度研究员，对主题进行深入调查。"
            "你收集相关信息，识别最佳实践，提供全面的研究发现和可执行建议。"
            "你严谨、基于证据、富有洞察力。"
        )

    @property
    def avatar_emoji(self) -> str:
        return "🔬"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        return (
            f"作为研究员Iris，分析这个主题：\n\n"
            f"主题: {task}\n\n"
            f"提供研究发现，包含:\n"
            f"- findings: 关键发现数组\n"
            f"- best_practices: 最佳实践数组\n"
            f"- recommendations: 总结建议字符串\n\n"
            f"输出JSON格式。"
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
