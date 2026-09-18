# ---------- SECTION 1: IMPORTS ----------
import os
import sys
import asyncio
from dotenv import load_dotenv
from beeai_framework.backend.chat import ChatModel
from beeai_framework.agents.react import ReActAgent
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.tools import tool


# ---------- SECTION 2: MODEL (Groq) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = ChatModel.from_name("groq:qwen/qwen3.8-27b", api_key=os.getenv("GROQ_API_KEY"))


# ---------- SECTION 3: A CUSTOM TOOL ----------
# The docstring is what the ReAct loop reads to decide when to call this.
@tool
def convert_currency(amount: float, rate: float) -> str:
    """Convert an amount of money using a given exchange rate.

    Args:
        amount: The amount of money to convert.
        rate: The exchange rate to multiply the amount by.
    """
    return f"{amount * rate:.2f}"


# ---------- SECTION 4: REACT AGENT ----------
# ReActAgent runs the classic Thought -> Action -> Observation loop until it
# has enough to answer, using the tool above whenever the math needs it.
agent = ReActAgent(llm=llm, tools=[convert_currency], memory=UnconstrainedMemory())


# ---------- SECTION 5: RUN ----------
async def main():
    result = await agent.run(
        "I have 120 US dollars. The exchange rate to EUR is 0.92. How many euros do I have?"
    )
    print(result.last_message.text)


if __name__ == "__main__":
    asyncio.run(main())
