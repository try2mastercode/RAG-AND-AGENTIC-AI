"""The LangGraph agent: an LLM node and a tool node in a loop.

    START -> agent --(tool calls?)--> tools -> agent -> ... -> END
"""
import os
from datetime import date

from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tools import TOOLS

GROQ_MODEL = os.getenv("GROQ_MODEL_AGENT", "qwen/qwen3.8-27b")

SYSTEM_PROMPT = """You are a task manager assistant. Today is {today}.

You help the user add, view, update, complete and delete tasks using your tools.
Rules:
- Convert relative dates ("tomorrow", "next Friday") to YYYY-MM-DD.
- If the user refers to a task by name, call list_tasks first to find its id.
- Never invent task ids.
- After a tool call, confirm what changed in one or two short sentences.
- If a request is not about tasks, answer briefly and steer back to tasks.
"""


def build_graph(model=None, checkpointer=None):
    if model is None:
        model = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)
    llm = model.bind_tools(TOOLS)

    def agent(state: MessagesState):
        system = SystemMessage(SYSTEM_PROMPT.format(today=date.today().isoformat()))
        response = llm.invoke([system, *state["messages"]])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agent")
    # tools_condition sends us to "tools" if the last message has tool calls, else END
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=checkpointer)
