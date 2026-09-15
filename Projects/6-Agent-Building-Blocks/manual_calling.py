import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)


# ---------- SECTION 1: TOOLS ----------
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


TOOLS = [get_weather, convert_currency, calculate]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}
llm_with_tools = llm.bind_tools(TOOLS)


# ---------- SECTION 2: THE BIND-TOOLS LOOP ----------
# bind_tools() only gives the model the tool schemas - it never runs a tool
# itself. This loop is what actually executes a call and feeds the result
# back, repeating until the model answers without requesting another tool.
# The same loop produces a single call, several parallel calls in one turn,
# or several dependent rounds - which one happens depends only on what the
# model decides for the question asked, not on any branching in this code.
def run_tool_calling(question: str, max_rounds: int = 4) -> dict:
    messages = [HumanMessage(question)]
    rounds = []

    for _ in range(max_rounds):
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        if not ai_msg.tool_calls:
            return {
                "rounds": rounds,
                "final_answer": ai_msg.content,
                "round_count": len(rounds),
            }

        calls = []
        for call in ai_msg.tool_calls:
            result = TOOLS_BY_NAME[call["name"]].invoke(call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
            calls.append({"tool": call["name"], "args": call["args"], "result": result})
        rounds.append(calls)

    return {"rounds": rounds, "final_answer": None, "round_count": len(rounds)}
