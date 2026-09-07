# ---------- SECTION 1: IMPORTS ----------
import os
import sys
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.tools import tool, StructuredTool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent


# ---------- SECTION 2: MODEL (Groq) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------- SECTION 3: TOOL DEFINITION, THREE WAYS ----------

# 3a. @tool with type hints - name/description/input+output types are all
# inferred from the function signature and docstring.
@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together and return the sum."""
    return a + b


# 3b. @tool with an explicit args_schema - use this when a field needs its
# own description/constraints beyond what a type hint can say.
class TemperatureInput(BaseModel):
    celsius: float = Field(description="Temperature in degrees Celsius")


@tool("celsius_to_fahrenheit", args_schema=TemperatureInput)
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32


# 3c. StructuredTool.from_function - builds a tool from a plain function
# without a decorator, useful when the function is defined/imported elsewhere.
def reverse_text(text: str) -> str:
    return text[::-1]


reverse_text_tool = StructuredTool.from_function(
    func=reverse_text,
    name="reverse_text",
    description="Reverse the characters in a string.",
)

tools = [add_numbers, celsius_to_fahrenheit, reverse_text_tool]


# ---------- SECTION 4: INSPECT A TOOL'S SCHEMA ----------
# Every tool carries the metadata the model actually sees: name, description,
# and a JSON schema for its inputs (derived from type hints or args_schema).
print("=== Tool schemas ===")
for t in tools:
    print(f"- {t.name}: {t.description} | args={t.args}")


# ---------- SECTION 5: BUILD AN ORCHESTRATING AGENT ----------
# create_agent wires the model + tools into a loop (LangGraph under the hood):
# the model decides which tool(s) to call, the graph executes them, feeds the
# results back, and repeats until the model answers without requesting a tool.
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant. Use tools whenever they help answer accurately.",
)


# ---------- SECTION 6: RUN THE AGENT ----------
# One prompt, three unrelated tools - the agent decides on its own which
# tools to call, in what order, with no manual tool-call loop written here.
print("\n=== Agent run ===")
result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                "Add 15 and 27, convert 100 celsius to fahrenheit, "
                "and reverse the word 'orchestration'."
            )
        ]
    }
)

for msg in result["messages"]:
    msg.pretty_print()
