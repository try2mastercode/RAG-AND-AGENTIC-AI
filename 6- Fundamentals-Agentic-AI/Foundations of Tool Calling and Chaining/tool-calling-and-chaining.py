

# ---------- SECTION 1: IMPORTS ----------
import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage


# ---------- SECTION 2: MODEL (Groq) ----------
# Requires GROQ_API_KEY (and optionally GROQ_MODEL) in .env
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")  # Windows console default (cp1252) can't print all model output

llm = ChatGroq(
    model="qwen/qwen3.8-27b",  # allam-2-7b (GROQ_MODEL) has no tool-calling support
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------- SECTION 3: DEFINE TOOLS ----------
# @tool turns a plain function into a schema the model can call. The docstring
# becomes the tool description the model reads to decide when to use it.
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    fake_weather_db = {
        "tokyo": "22°C, clear skies",
        "paris": "14°C, light rain",
        "new york": "9°C, cloudy",
    }
    return fake_weather_db.get(city.lower(), "Unknown city")


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another."""
    fake_rates = {("USD", "JPY"): 155.0, ("USD", "EUR"): 0.92}
    rate = fake_rates.get((from_currency.upper(), to_currency.upper()))
    if rate is None:
        return f"No rate available for {from_currency} -> {to_currency}"
    return f"{amount} {from_currency} = {amount * rate:.2f} {to_currency}"


@tool
def calculate(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * (4 + 1)'."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: expression contains disallowed characters"
    return str(eval(expression))


tools = [get_weather, convert_currency, calculate]


# ---------- SECTION 4: BIND TOOLS TO THE MODEL ----------
# The model itself never runs the tools - bind_tools() just gives it the
# schemas so it can decide *when* to ask for a call and *what* arguments to pass.
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


# ---------- SECTION 5: SINGLE TOOL CALL (ask -> call -> answer) ----------
print("=== Single tool call ===")
messages = [HumanMessage("What's the weather in Tokyo?")]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

for call in ai_msg.tool_calls:
    result = tools_by_name[call["name"]].invoke(call["args"])
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

final = llm_with_tools.invoke(messages)
print(final.content)


# ---------- SECTION 6: PARALLEL TOOL CALLS (one turn, independent calls) ----------
# When a request needs several unrelated lookups, the model can emit multiple
# tool_calls in a single AIMessage instead of one call per round trip.
print("\n=== Parallel tool calls ===")
messages = [HumanMessage("What's the weather in Tokyo and in Paris?")]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

for call in ai_msg.tool_calls:
    result = tools_by_name[call["name"]].invoke(call["args"])
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

final = llm_with_tools.invoke(messages)
print(final.content)


# ---------- SECTION 7: CHAINED TOOL CALLS (agent loop, dependent calls) ----------
# Here the second tool call depends on the first tool's result (only convert
# currency if it's warm), so the model can't decide both calls up front - it
# needs the loop to keep going until it stops asking for tools.
print("\n=== Chained tool calls ===")
messages = [
    HumanMessage(
        "Check the weather in Tokyo. If it's above 20°C, convert 100 USD to JPY "
        "for my trip budget."
    )
]

while True:
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    if not ai_msg.tool_calls:
        break

    for call in ai_msg.tool_calls:
        result = tools_by_name[call["name"]].invoke(call["args"])
        print(f"  -> called {call['name']}({call['args']}) = {result}")
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

print(ai_msg.content)
