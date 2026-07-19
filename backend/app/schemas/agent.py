from pydantic import BaseModel
from typing import Optional, Any


class AgentThinkResult(BaseModel):
    agent_name: str
    thought: str


class AgentActResult(BaseModel):
    agent_name: str
    action: str
    output: str


class AgentExecuteResult(BaseModel):
    agent_name: str
    thought: str
    action: str
    output: str
    duration_ms: int


class OrchestratorPlan(BaseModel):
    mode: str
    steps: list[dict[str, Any]]
