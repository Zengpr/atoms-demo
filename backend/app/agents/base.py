from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
from app.utils.llm import llm_provider


class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def role(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def avatar_emoji(self) -> str: ...

    @abstractmethod
    async def think(self, task: str, context: dict[str, Any]) -> str: ...

    @abstractmethod
    async def act(self, task: str, context: dict[str, Any]) -> str: ...

    async def execute(self, task: str, context: dict[str, Any]) -> tuple[str, str]:
        thought = await self.think(task, context)
        action = await self.act(task, {**context, "thought": thought})
        return thought, action

    async def think_stream(self, task: str, context: dict[str, Any]) -> AsyncIterator[str]:
        prompt = self._build_think_prompt(task, context)
        full = ""
        if llm_provider.is_mock:
            result = await self.think(task, context)
            words = result.split(" ")
            for i, w in enumerate(words):
                chunk = w + (" " if i < len(words) - 1 else "")
                full += chunk
                yield chunk
            return
        async for chunk in llm_provider.generate_stream(self.get_system_prompt(), prompt):
            full += chunk
            yield chunk

    async def act_stream(self, task: str, context: dict[str, Any]) -> AsyncIterator[str]:
        prompt = self._build_act_prompt(task, context)
        full = ""
        if llm_provider.is_mock:
            result = await self.act(task, context)
            words = result.split(" ")
            for i, w in enumerate(words):
                chunk = w + (" " if i < len(words) - 1 else "")
                full += chunk
                yield chunk
            return
        async for chunk in llm_provider.generate_stream(self.get_system_prompt(), prompt, temperature=0.4):
            full += chunk
            yield chunk

    def get_system_prompt(self) -> str:
        return f"You are {self.name}, {self.role}. {self.description}"

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        return f"Request: {task}\n\nDescribe your implementation plan briefly (2-3 sentences)."

    def _build_act_prompt(self, task: str, context: dict[str, Any]) -> str:
        return f"Implement a COMPLETE, WORKING web application for:\n\nRequest: {task}\n\nOutput ONLY the HTML code, no markdown code fences, no explanation."
