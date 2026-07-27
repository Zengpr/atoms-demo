import json
from typing import Any
from app.agents.base import BaseAgent
from app.utils.llm import llm_provider


class LeaderAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Mike"

    @property
    def role(self) -> str:
        return "团队负责人 & 协调者"

    @property
    def description(self) -> str:
        return (
            "你是团队负责人，负责协调整个开发流程。"
            "你分析用户需求，将其分解为任务，并分配给合适的团队成员。"
            "你确保所有交付物的质量和一致性。你果断、有条理、善于沟通。"
        )

    @property
    def avatar_emoji(self) -> str:
        return "👨‍💼"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        return (
            f"作为团队负责人Mike，分析这个请求并制定执行计划：\n\n"
            f"用户请求: {task}\n\n"
            f"项目模式: {context.get('mode', 'team')}\n\n"
            f"可用Agent:\n"
            f"- Emma (产品经理): 需求分析、PRD生成\n"
            f"- Bob (架构师): 系统设计、技术选型\n"
            f"- Alex (工程师): 代码实现\n"
            f"- Iris (研究员): 深度研究\n\n"
            f"决定需要哪些Agent参与以及执行顺序。"
            f"输出JSON计划，包含'plan'(摘要)、'steps'(数组，每项{{agent, task}})、"
            f"'summary'(一句话总结)。"
        )

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_think_prompt(task, context)
        if llm_provider.is_mock:
            return json.dumps({
                "plan": "I'll coordinate the team to build this application step by step.",
                "steps": [
                    {"agent": "pm", "task": f"Analyze requirements for: {task}"},
                    {"agent": "architect", "task": f"Design architecture for: {task}"},
                    {"agent": "engineer", "task": f"Implement: {task}"}
                ],
                "summary": "Full team pipeline: PM → Architect → Engineer"
            })
        result = await llm_provider.generate(self.get_system_prompt(), prompt)
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            return json.dumps({
                "plan": "I'll coordinate the team to build this application step by step.",
                "steps": [
                    {"agent": "pm", "task": f"Analyze requirements for: {task}"},
                    {"agent": "architect", "task": f"Design architecture for: {task}"},
                    {"agent": "engineer", "task": f"Implement: {task}"}
                ],
                "summary": "Full team pipeline: PM → Architect → Engineer"
            })

    async def act(self, task: str, context: dict[str, Any]) -> str:
        thought = context.get("thought", "")
        try:
            plan_data = json.loads(thought)
            return json.dumps(plan_data)
        except json.JSONDecodeError:
            return thought
