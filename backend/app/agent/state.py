from pydantic import BaseModel, Field
from typing import Any
class AgentState(BaseModel):
    question: str
    service: str
    logs: list = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)
    deployments: list = Field(default_factory=list)
    rag_evidence: list = Field(default_factory=list)
    hypothesis: str = ""
    final_answer: str = ""
    messages: list[Any] = Field(default_factory=list)
