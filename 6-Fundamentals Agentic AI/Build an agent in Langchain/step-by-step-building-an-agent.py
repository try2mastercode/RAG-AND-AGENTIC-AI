# ---------- STEP 1: IMPORTS ----------
import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver


# ---------- STEP 2: DECIDE WHAT THE AGENT NEEDS - DEFINE ITS TOOLS ----------
# An agent is only as capable as the tools it's given. Each @tool becomes a
# schema (name, description, arguments) the model can choose to call.
@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its order ID."""
    fake_orders = {"A100": "Shipped, arriving in 2 days", "A101": "Processing"}
    return fake_orders.get(order_id.upper(), "Order not found")


@tool
def issue_refund(order_id: str, reason: str) -> str:
    """Issue a refund for an order, given a reason."""
    return f"Refund issued for order {order_id.upper()} - reason: {reason}"


tools = [get_order_status, issue_refund]


# ---------- STEP 3: CHOOSE AND CONFIGURE THE LLM ----------
# The LLM is the agent's decision-maker - it reads the conversation and tool
# results, and decides what to do next (call a tool, or answer).
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = ChatGroq(
    model="qwen/qwen3.8-27b",  # allam-2-7b (GROQ_MODEL) has no tool-calling support
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------- STEP 4: GIVE THE AGENT A PERSONA - THE SYSTEM PROMPT ----------
# The system prompt sets the agent's role and boundaries. Without it, the
# model has no instruction to prefer tools over guessing.
system_prompt = (
    "You are a customer support agent for an online store. "
    "Always use the available tools to look up real order information "
    "instead of guessing. Keep answers short and polite."
)


# ---------- STEP 5: ASSEMBLE THE AGENT ----------
# create_agent wires the model, tools, and system prompt into a LangGraph
# loop: the model reads the conversation, optionally calls tools, the graph
# executes them and feeds results back, and this repeats until the model
# responds without requesting another tool call.
agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)


# ---------- STEP 6: RUN THE AGENT AND WATCH EACH STEP ----------
# .stream() (instead of .invoke()) yields one update per step of the loop,
# so you can see the model's tool call and the tool's result as they happen
# rather than only the final answer.
print("=== Step-by-step agent run (streamed) ===")
for step in agent.stream(
    {"messages": [HumanMessage("What's the status of order A100?")]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()


# ---------- STEP 7: ADD MEMORY SO THE AGENT REMEMBERS EARLIER TURNS ----------
# Without a checkpointer, every .invoke() call starts fresh with no memory
# of prior turns. A checkpointer persists conversation state per thread_id,
# so follow-up questions can refer back to earlier ones.
agent_with_memory = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
)
conversation_config = {"configurable": {"thread_id": "customer-42"}}


# ---------- STEP 8: RUN A MULTI-TURN CONVERSATION USING THAT MEMORY ----------
print("\n=== Multi-turn conversation (memory across calls) ===")
turn_1 = agent_with_memory.invoke(
    {"messages": [HumanMessage("What's the status of order A101?")]},
    config=conversation_config,
)
print("User: What's the status of order A101?")
print("Agent:", turn_1["messages"][-1].content)

turn_2 = agent_with_memory.invoke(
    {"messages": [HumanMessage("Actually, please refund that order - it's late.")]},
    config=conversation_config,
)
print("\nUser: Actually, please refund that order - it's late.")
print("Agent:", turn_2["messages"][-1].content)
