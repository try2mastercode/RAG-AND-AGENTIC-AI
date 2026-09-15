import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)


# ---------- SECTION 1: TOOLS ----------
@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its order ID."""
    fake_orders = {"A100": "Shipped, arriving in 2 days", "A101": "Processing"}
    return fake_orders.get(order_id.upper(), "Order not found")


@tool
def issue_refund(order_id: str, reason: str) -> str:
    """Issue a refund for an order, given a reason."""
    return f"Refund issued for order {order_id.upper()} - reason: {reason}"


TOOLS = [get_order_status, issue_refund]

SYSTEM_PROMPT = (
    "You are a customer support agent for an online store. "
    "Always use the available tools to look up real order information "
    "instead of guessing. Keep answers short and polite."
)


# ---------- SECTION 2: ONE-OFF AGENT (no memory) - WATCH EACH STEP ----------
agent = create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)


def run_traced(question: str) -> dict:
    steps = []
    for update in agent.stream({"messages": [HumanMessage(question)]}, stream_mode="values"):
        msg = update["messages"][-1]
        if isinstance(msg, AIMessage) and msg.tool_calls:
            steps.append({"role": "agent", "tool_calls": [
                {"tool": c["name"], "args": c["args"]} for c in msg.tool_calls
            ]})
        elif isinstance(msg, ToolMessage):
            steps.append({"role": "tool", "name": msg.name, "result": msg.content})
        elif isinstance(msg, AIMessage):
            steps.append({"role": "agent", "final_answer": msg.content})
    return {"steps": steps}


# ---------- SECTION 3: AGENT WITH MEMORY - MULTI-TURN CONVERSATION ----------
# Without a checkpointer every invoke() starts fresh. InMemorySaver persists
# state per thread_id, so a follow-up like "refund that order" can resolve
# "that order" from what was said earlier in the same thread.
agent_with_memory = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)


def chat(thread_id: str, message: str) -> str:
    result = agent_with_memory.invoke(
        {"messages": [HumanMessage(message)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return result["messages"][-1].content
