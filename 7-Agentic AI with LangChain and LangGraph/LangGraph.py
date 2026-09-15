# LangGraph from scratch: run this file top to bottom, read the section you're on.
# Every section is a self-contained demo function; main() at the bottom runs them in order.


# ---------- SECTION 1: IMPORTS ----------
import os
import operator
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"
HAVE_KEY = bool(os.getenv("GROQ_API_KEY"))  # LLM sections are skipped if this is missing


# ---------- SECTION 2: THE CORE IDEA ----------
# A LangGraph graph = a State (shared data, usually a TypedDict) + Nodes (plain functions
# that take the state and return a partial update) + Edges (which node runs next).
# You build it with StateGraph, wire nodes/edges, then .compile() it into a runnable app.


# ---------- SECTION 3: SIMPLEST POSSIBLE GRAPH (one node) ----------
class GreetState(TypedDict):
    name: str
    greeting: str


def make_greeting(state: GreetState) -> GreetState:
    return {"greeting": f"Hello, {state['name']}!"}  # a node returns only the keys it changes


def demo_simplest_graph():
    graph = StateGraph(GreetState)
    graph.add_node("greet", make_greeting)
    graph.add_edge(START, "greet")   # START -> greet
    graph.add_edge("greet", END)     # greet -> END
    app = graph.compile()
    print(app.invoke({"name": "Tharun", "greeting": ""}))


# ---------- SECTION 4: CHAINING MULTIPLE NODES ----------
class TextState(TypedDict):
    text: str


def to_upper(state: TextState) -> TextState:
    return {"text": state["text"].upper()}


def add_exclaim(state: TextState) -> TextState:
    return {"text": state["text"] + "!!!"}


def demo_chained_nodes():
    graph = StateGraph(TextState)
    graph.add_node("upper", to_upper)
    graph.add_node("exclaim", add_exclaim)
    graph.add_edge(START, "upper")
    graph.add_edge("upper", "exclaim")   # output of "upper" becomes the input of "exclaim"
    graph.add_edge("exclaim", END)
    app = graph.compile()
    print(app.invoke({"text": "langgraph is fun"}))


# ---------- SECTION 5: CONDITIONAL EDGES (branching) ----------
class NumberState(TypedDict):
    n: int
    label: str


def route_by_parity(state: NumberState) -> str:
    return "even" if state["n"] % 2 == 0 else "odd"   # this return value picks the next node


def mark_even(state: NumberState) -> NumberState:
    return {"label": "even"}


def mark_odd(state: NumberState) -> NumberState:
    return {"label": "odd"}


def demo_conditional_edges():
    graph = StateGraph(NumberState)
    graph.add_node("even", mark_even)
    graph.add_node("odd", mark_odd)
    graph.add_conditional_edges(START, route_by_parity, {"even": "even", "odd": "odd"})  # branch right from the start
    graph.add_edge("even", END)
    graph.add_edge("odd", END)
    app = graph.compile()
    print(app.invoke({"n": 7, "label": ""}))


# ---------- SECTION 6: LOOPS (cycle back to a node until a condition is met) ----------
class CounterState(TypedDict):
    count: int


def increment(state: CounterState) -> CounterState:
    return {"count": state["count"] + 1}


def should_continue(state: CounterState) -> str:
    return "loop" if state["count"] < 5 else "stop"


def build_counter_graph():
    graph = StateGraph(CounterState)
    graph.add_node("increment", increment)
    graph.add_edge(START, "increment")
    graph.add_conditional_edges("increment", should_continue, {"loop": "increment", "stop": END})
    return graph.compile()


def demo_loop():
    print(build_counter_graph().invoke({"count": 0}))


# ---------- SECTION 7: REDUCERS (how state updates get merged) ----------
# By default a node's return value OVERWRITES that key. Annotated + operator.add makes
# LangGraph accumulate instead — each node's list gets appended to the running one.
class LogState(TypedDict):
    log: Annotated[list[str], operator.add]


def step_one(state: LogState) -> LogState:
    return {"log": ["step one ran"]}


def step_two(state: LogState) -> LogState:
    return {"log": ["step two ran"]}


def demo_reducer():
    graph = StateGraph(LogState)
    graph.add_node("one", step_one)
    graph.add_node("two", step_two)
    graph.add_edge(START, "one")
    graph.add_edge("one", "two")
    graph.add_edge("two", END)
    app = graph.compile()
    print(app.invoke({"log": []}))   # log ends up with BOTH entries, not just the last one


# ---------- SECTION 8: STREAMING (watch state change step by step) ----------
def demo_streaming():
    app = build_counter_graph()
    for step in app.stream({"count": 0}):
        print(step)   # each step is {node_name: state_returned_by_that_node}


# ---------- SECTION 9: GIVING A NODE AN LLM ----------
def demo_llm_node():
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): demo_llm_node")
        return
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)

    def chat_node(state: MessagesState) -> MessagesState:
        return {"messages": [llm.invoke(state["messages"])]}
        # MessagesState already has a built-in reducer, so messages accumulate automatically

    graph = StateGraph(MessagesState)
    graph.add_node("chat", chat_node)
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)
    app = graph.compile()
    result = app.invoke({"messages": [HumanMessage("Say hello in exactly 5 words.")]})
    print(result["messages"][-1].content)


# ---------- SECTION 10: TOOLS + A REAL AGENT LOOP (ReAct pattern) ----------
@tool
def add_numbers(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


@tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two integers together."""
    return a * b


TOOLS = [add_numbers, multiply_numbers]


def demo_tool_calling_agent():
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): demo_tool_calling_agent")
        return
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0).bind_tools(TOOLS)

    def agent_node(state: MessagesState) -> MessagesState:
        return {"messages": [llm.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)  # -> "tools" if the LLM asked for a tool, else END
    graph.add_edge("tools", "agent")   # after running the tool, go back and let the LLM read the result
    app = graph.compile()
    result = app.invoke({"messages": [HumanMessage("What is 12 plus 30, then that result times 2?")]})
    print(result["messages"][-1].content)


# ---------- SECTION 11: MEMORY (checkpointing across turns) ----------
def demo_memory():
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): demo_memory")
        return
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)

    def chat_node(state: MessagesState) -> MessagesState:
        return {"messages": [llm.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("chat", chat_node)
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)
    checkpointer = MemorySaver()   # stores each thread's state in RAM (use SQLite/Postgres savers to persist to disk)
    app = graph.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "demo-thread-1"}}   # same thread_id = same remembered conversation
    app.invoke({"messages": [HumanMessage("My name is Tharun.")]}, config)
    result = app.invoke({"messages": [HumanMessage("What is my name?")]}, config)
    print(result["messages"][-1].content)


# ---------- SECTION 12: THE PREBUILT SHORTCUT ----------
# create_agent builds the exact agent/tools loop from Section 10 for you in one line.
def demo_prebuilt_react_agent():
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): demo_prebuilt_react_agent")
        return
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)
    app = create_agent(llm, TOOLS)
    result = app.invoke({"messages": [HumanMessage("What is 7 times 6?")]})
    print(result["messages"][-1].content)


# ---------- SECTION 13: MULTI-AGENT (a supervisor routing to specialist agents) ----------
class RouteState(MessagesState):
    next: str


def demo_multi_agent_supervisor():
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): demo_multi_agent_supervisor")
        return
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)

    def supervisor(state: RouteState) -> RouteState:
        last_message = state["messages"][-1].content.lower()
        decision = "math_agent" if any(ch.isdigit() for ch in last_message) else "writer_agent"
        return {"next": decision}

    def math_agent(state: RouteState) -> RouteState:
        response = llm.invoke([SystemMessage("You only answer math questions, briefly."), *state["messages"]])
        return {"messages": [response]}

    def writer_agent(state: RouteState) -> RouteState:
        response = llm.invoke([SystemMessage("You only write one short creative sentence."), *state["messages"]])
        return {"messages": [response]}

    graph = StateGraph(RouteState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("math_agent", math_agent)
    graph.add_node("writer_agent", writer_agent)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", lambda s: s["next"], {"math_agent": "math_agent", "writer_agent": "writer_agent"})
    graph.add_edge("math_agent", END)
    graph.add_edge("writer_agent", END)
    app = graph.compile()

    print(app.invoke({"messages": [HumanMessage("What is 45 divided by 9?")], "next": ""})["messages"][-1].content)
    print(app.invoke({"messages": [HumanMessage("Write a line about the ocean.")], "next": ""})["messages"][-1].content)


# ---------- SECTION 14: HUMAN-IN-THE-LOOP (pause the graph, wait for a human, resume) ----------
class ApprovalState(TypedDict):
    amount: int
    approved: bool


def request_approval(state: ApprovalState) -> ApprovalState:
    decision = interrupt(f"Approve spending {state['amount']}? (True/False)")  # graph pauses here
    return {"approved": decision}


def demo_human_in_the_loop():
    graph = StateGraph(ApprovalState)
    graph.add_node("approve", request_approval)
    graph.add_edge(START, "approve")
    graph.add_edge("approve", END)
    app = graph.compile(checkpointer=MemorySaver())   # a checkpointer is required to pause/resume

    config = {"configurable": {"thread_id": "approval-1"}}
    paused = app.invoke({"amount": 500, "approved": False}, config)
    print(paused)                                      # contains "__interrupt__" with the question above
    result = app.invoke(Command(resume=True), config)   # human answers "True" -> graph continues from where it paused
    print(result)


# ---------- SECTION 15: VISUALIZING A GRAPH ----------
def demo_visualize():
    print(build_counter_graph().get_graph().draw_mermaid())   # paste the output into https://mermaid.live


# ---------- MAIN: run every section in order ----------
def main():
    sections = [
        ("3  Simplest graph", demo_simplest_graph),
        ("4  Chained nodes", demo_chained_nodes),
        ("5  Conditional edges", demo_conditional_edges),
        ("6  Loop", demo_loop),
        ("7  Reducers", demo_reducer),
        ("8  Streaming", demo_streaming),
        ("9  LLM node", demo_llm_node),
        ("10 Tool-calling agent", demo_tool_calling_agent),
        ("11 Memory", demo_memory),
        ("12 Prebuilt ReAct agent", demo_prebuilt_react_agent),
        ("13 Multi-agent supervisor", demo_multi_agent_supervisor),
        ("14 Human-in-the-loop", demo_human_in_the_loop),
        ("15 Visualize", demo_visualize),
    ]
    for title, fn in sections:
        print(f"\n=== SECTION {title} ===")
        fn()


if __name__ == "__main__":
    main()
