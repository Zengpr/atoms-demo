import json
from typing import Any
from app.agents.base import BaseAgent
from app.utils.llm import llm_provider


class ArchitectAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Bob"

    @property
    def role(self) -> str:
        return "系统架构师"

    @property
    def description(self) -> str:
        return (
            "你是资深系统架构师，设计健壮、可扩展的系统架构。"
            "你选择合适的技术栈，定义组件结构，创建指导实现的架构文档。"
            "你善于分析、前瞻和务实。"
        )

    @property
    def avatar_emoji(self) -> str:
        return "🏗️"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        prd = context.get("prd", "")
        prompt = (
            f"作为架构师Bob，为此项目设计架构：\n\n"
            f"请求: {task}\n\n"
            f"PRD: {prd}\n\n"
            f"创建架构文档，包含:\n"
            f"- tech_stack: {{frontend, styling, icons}} 用于Web应用\n"
            f"- component_structure: 数组，每项{{name, description}}\n"
            f"- design_system: {{colors, typography, spacing, border_radius}}\n\n"
            f"因为生成的Web应用在iframe中渲染，使用HTML5 + CSS3 + 原生JS。\n"
            f"输出JSON格式。"
        )
        return prompt

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_think_prompt(task, context)
        if llm_provider.is_mock:
            from app.utils.llm import MOCK_RESPONSES
            return MOCK_RESPONSES.get("architect", "")
        result = await llm_provider.generate(self.get_system_prompt(), prompt)
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            return result

    async def act(self, task: str, context: dict[str, Any]) -> str:
        thought = context.get("thought", "")
        try:
            arch = json.loads(thought)
            return json.dumps(arch)
        except json.JSONDecodeError:
            return thought
