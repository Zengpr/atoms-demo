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
        return "System Architect"

    @property
    def description(self) -> str:
        return (
            "You are a senior System Architect who designs robust, scalable system architectures. "
            "You select appropriate tech stacks, define component structures, and create "
            "architecture documents that guide implementation. You are analytical, "
            "forward-thinking, and pragmatic."
        )

    @property
    def avatar_emoji(self) -> str:
        return "🏗️"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        prd = context.get("prd", "")
        prompt = (
            f"As Bob the Architect, design the architecture for this project:\n\n"
            f"Request: {task}\n\n"
            f"PRD: {prd}\n\n"
            f"Create an architecture document with:\n"
            f"- tech_stack: {{frontend, styling, icons}} for web apps\n"
            f"- component_structure: Array of {{name, description}}\n"
            f"- design_system: {{colors, typography, spacing, border_radius}}\n\n"
            f"Since this generates web apps rendered in iframes, use HTML5 + CSS3 + vanilla JS.\n"
            f"Output as JSON."
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
