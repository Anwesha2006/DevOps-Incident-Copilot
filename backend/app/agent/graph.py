from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.tools import (
    search_incident_docs,
    search_logs,
    get_metrics,
    get_recent_deployments,
)


# -------------------------
# LLM
# -------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=0,
    timeout=30
)


# -------------------------
# Tools
# -------------------------

tools = [
    search_incident_docs,
    search_logs,
    get_metrics,
    get_recent_deployments,
]

llm_with_tools = llm.bind_tools(tools)


# -------------------------
# Agent node
# -------------------------

def agent_node(state: AgentState):

    print("\n[AGENT] Calling Groq...")

    system_prompt = """
You are a careful DevOps incident investigator.

Your job is to investigate production incidents using available tools.

You should:
1. Search relevant incident documentation when useful.
2. Search logs for evidence.
3. Check service metrics.
4. Check recent deployments.
5. Compare the evidence.
6. Form a root-cause hypothesis only when supported by evidence.
7. Do not invent facts.
8. Once you have enough evidence, provide a concise final answer.

Do not repeatedly call the same tool with the same arguments.
"""

    messages = [
        SystemMessage(content=system_prompt)
    ] + list(state.messages)

    response = llm_with_tools.invoke(messages)

    print("[AGENT] Groq response received")
    print("[AGENT] Tool calls:", response.tool_calls)

    return {
        "messages": [response]
    }


# -------------------------
# Build graph
# -------------------------

def build_graph(checkpointer=None):

    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)

    graph.add_node(
        "tools",
        ToolNode(tools)
    )

    # Start
    graph.add_edge(START, "agent")

    # Agent decides:
    # tool call -> tools
    # no tool call -> END
    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )

    # After tool execution, go back to agent
    graph.add_edge("tools", "agent")

    return graph.compile(
        checkpointer=checkpointer
    )


# -------------------------
# Run graph
# -------------------------

def run_graph(question: str, service: str):

    app = build_graph()

    initial_state = {
        "question": question,
        "service": service,

        "messages": [
            HumanMessage(
                content=f"""
Investigate this incident:

Question: {question}
Service: {service}
"""
            )
        ],

        "logs": [],
        "metrics": {},
        "deployments": [],
        "rag_evidence": [],
        "hypothesis": "",
        "final_answer": "",
    }

    result = app.invoke(
        initial_state,
        config={
            "recursion_limit": 15
        }
    )

    return result


# -------------------------
# Main
# -------------------------

if __name__ == "__main__":

    question = input(
        "Enter incident question: "
    )

    service = input(
        "Enter service name: "
    )

    result = run_graph(
        question,
        service
    )

    print("\n")
    print("=" * 60)
    print("AGENT RESULT")
    print("=" * 60)

    messages = result["messages"]

    final_message = messages[-1]

    print(final_message.content)