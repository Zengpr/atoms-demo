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
        return "产品经理"

    @property
    def description(self) -> str:
        return (
            "你是资深产品经理，擅长理解用户需求并将其转化为清晰、可执行的产品需求。"
            "你创建详细的PRD，包含功能、用户故事和验收标准。"
            "你富有同理心、注重细节、以用户为中心。"
        )

    @property
    def avatar_emoji(self) -> str:
        return "👩‍💻"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        return (
            f"作为产品经理Emma，分析这个请求并创建PRD：\n\n"
            f"请求: {task}\n\n"
            f"创建产品需求文档，包含:\n"
            f"- title: PRD标题\n"
            f"- overview: 产品概述\n"
            f"- features: 数组，每项{{name, description, priority}}\n"
            f"- user_stories: 用户故事字符串数组\n"
            f"- acceptance_criteria: 验收标准字符串数组\n\n"
            f"输出JSON格式。"
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
