from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(BaseModel):
    question: str
    service: str

    messages: Annotated[list[AnyMessage], add_messages] = Field(
        default_factory=list
    )

    logs: list = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)
    deployments: list = Field(default_factory=list)
    rag_evidence: list = Field(default_factory=list)

    hypothesis: str = ""
    final_answer: str = ""