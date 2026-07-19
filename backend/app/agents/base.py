from abc import ABC, abstractmethod
from typing import Any


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

    def get_system_prompt(self) -> str:
        return f"You are {self.name}, {self.role}. {self.description}"
