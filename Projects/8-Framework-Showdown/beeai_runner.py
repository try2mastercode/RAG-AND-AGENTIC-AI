"""Runs inside the C:\\v8\\beeai Python 3.11 venv, launched as a subprocess by
app.py — see crewai_runner.py's docstring for why this needs its own
interpreter. Talks to app.py over stdin/stdout JSON only.
"""
import asyncio
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from beeai_framework.backend.chat import ChatModel
from beeai_framework.agents.react import ReActAgent
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.tools import tool

_tool_calls: list[dict] = []


# The docstring is what the ReAct loop reads to decide when to call this.
@tool
def convert_currency(amount: float, rate: float) -> str:
    """Convert an amount of money using a given exchange rate.

    Args:
        amount: The amount of money to convert.
        rate: The exchange rate to multiply the amount by.
    """
    result = f"{amount * rate:.2f}"
    _tool_calls.append({"amount": amount, "rate": rate, "result": result})
    return result


async def run(question: str) -> dict:
    llm = ChatModel.from_name("groq:qwen/qwen3.8-27b", api_key=os.getenv("GROQ_API_KEY"))
    agent = ReActAgent(llm=llm, tools=[convert_currency], memory=UnconstrainedMemory())
    result = await agent.run(question)
    return {
        "answer": result.last_message.text,
        "tool_calls": _tool_calls,
        "tool": {"name": convert_currency.name, "description": convert_currency.description},
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    payload = json.loads(sys.argv[1])
    print(json.dumps(asyncio.run(run(payload["question"]))))
