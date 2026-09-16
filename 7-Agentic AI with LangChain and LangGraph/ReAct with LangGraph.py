# ReAct agent from scratch: run this file top to bottom, read the section you're on.


# ---------- SECTION 1: IMPORTS ----------
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"
HAVE_KEY = bool(os.getenv("GROQ_API_KEY"))


# ---------- SECTION 2: THE CORE IDEA ----------
# ReAct (Yao et al., 2022) interleaves Reasoning and Acting: the LLM alternates between
# a "Thought" (plan the next step), an "Action" (call a tool) and an "Observation" (the
# tool's result), looping until it has enough to give a Final Answer. With LangChain tool
# calling, the loop is just: agent node thinks + optionally calls tools -> tools node runs
# them -> back to agent with the observation appended -> repeat until no tool call is made.


# ---------- SECTION 3: TOOLS ----------
CITY_POPULATIONS = {"paris": 2_100_000, "tokyo": 13_960_000, "cairo": 10_100_000}


@tool
def get_population(city: str) -> str:
    """Look up a city's population. City name must be one of: paris, tokyo, cairo."""
    pop = CITY_POPULATIONS.get(city.lower())
    return f"{pop}" if pop else f"No population data for {city}."


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression, e.g. '2100000 / 2 + 100'."""
    return str(eval(expression, {"__builtins__": {}}))


TOOLS = [get_population, calculator]


# ---------- SECTION 4: GRAPH (agent node + tools node, looping) ----------
SYSTEM_PROMPT = SystemMessage(
    "You are a ReAct agent. Before every tool call, briefly state your Thought "
    "(one sentence). When you have the final answer, reply with it directly "
    "and do not call any more tools."
)


def build_graph():
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0).bind_tools(TOOLS)

    def agent_node(state: MessagesState) -> MessagesState:
        return {"messages": [llm.invoke([SYSTEM_PROMPT, *state["messages"]])]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)  # -> "tools" if a tool was called, else END
    graph.add_edge("tools", "agent")   # observation goes back to the agent to think again
    return graph.compile()


# ---------- SECTION 5: DEMO (stream so each Thought/Action/Observation is visible) ----------
def run_react_agent(question: str):
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): run_react_agent")
        return
    app = build_graph()

    for step in app.stream({"messages": [HumanMessage(question)]}):
        for node_name, update in step.items():
            message = update["messages"][-1]
            if node_name == "agent":
                if message.tool_calls:
                    for call in message.tool_calls:
                        print(f"Thought/Action: call {call['name']}({call['args']})")
                else:
                    print(f"Final Answer: {message.content}")
            else:
                print(f"Observation: {message.content}")


def main():
    run_react_agent("What is the population of Tokyo, divided by 2, plus 100?")


if __name__ == "__main__":
    main()
