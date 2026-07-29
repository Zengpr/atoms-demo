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
            "You are a senior system architect, designing robust and scalable system architectures. "
            "You choose the right tech stack, define component structures, and create architecture documents that guide implementation. "
            "You are analytical, forward-thinking, and pragmatic."
        )

    @property
    def avatar_emoji(self) -> str:
        return "🏗️"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        prd = context.get("prd", "")
        original_request = context.get("original_request", task)
        prompt = (
            f"As architect Bob, design the architecture for this project:\n\n"
            f"ORIGINAL USER REQUEST: {original_request}\n"
            f"YOUR ASSIGNMENT: {task}\n\n"
            f"CRITICAL: Design architecture for the EXACT product the user requested. "
            f"If they asked for a calculator, design a calculator — NOT a different product.\n\n"
            f"PRD: {prd}\n\n"
            f"Create an architecture document with:\n"
            f"- tech_stack: {{frontend, styling, icons}} for the web app\n"
            f"- component_structure: Array of {{name, description}} — components for THIS specific product\n"
            f"- design_system: {{colors, typography, spacing, border_radius}}\n\n"
            f"Since the generated web app renders in an iframe, use HTML5 + CSS3 + vanilla JS.\n"
            f"Output in JSON format."
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
