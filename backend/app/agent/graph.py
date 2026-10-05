from app.agent.state import AgentState
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.tools import (
    search_incident_docs,
    search_logs,
    get_metrics,
    get_recent_deployments
)
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)
tools = [
    search_incident_docs,
    search_logs,
    get_metrics,
    get_recent_deployments
]
llm_with_tools = llm.bind_tools(tools)
def agent_node(state: AgentState):

    system_prompt = """
You are a DevOps Incident Investigation Agent.

Your job is to investigate production incidents using
the available tools.

Available tools:

- search_incident_docs
  Search historical incident documentation.

- search_logs
  Search current service logs.

- get_metrics
  Retrieve operational metrics.

- get_recent_deployments
  Retrieve recent deployments.

Rules:

1. Gather evidence before forming a root-cause hypothesis.
2. Do not invent facts.
3. Use tools when additional evidence is required.
4. You may call multiple tools.
5. Once enough evidence is available, provide a final answer.
6. Clearly distinguish evidence from hypothesis.
"""

    user_prompt = f"""
Incident question:
{state.question}

Affected service:
{state.service}

Previously collected logs:
{state.logs}

Previously collected metrics:
{state.metrics}

Previously collected deployments:
{state.deployments}

Previously collected RAG evidence:
{state.rag_evidence}

Current hypothesis:
{state.hypothesis}
"""
    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return {
        "messages": [response]
    }

def build_graph(checkpointer=None):
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools",ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )
    graph.add_edge("tools","agent")
    return graph.compile(checkpointer=checkpointer)
def run_graph(question: str, service: str):
    app = build_graph()
    initial_state = {
        "question": question,
        "service": service,
        "logs": [],
        "metrics": {},
        "deployments": [],
        "rag_evidence": [],
        "hypothesis": "",
        "final_answer": ""
    }
    result = app.invoke(initial_state)
    return result
if __name__ == "__main__":
    question = input("Enter incident question: ")
    service = input("Enter service name: ")
    result = run_graph(
        question,
        service
    )
    print("\n")
    print("=" * 60)
    print("AGENT RESULT")
    print("=" * 60)
    print(result)