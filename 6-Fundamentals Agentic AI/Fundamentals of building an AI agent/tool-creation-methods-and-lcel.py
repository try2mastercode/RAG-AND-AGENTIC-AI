# ---------- SECTION 1: IMPORTS ----------
import os
import sys
from typing import Type
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.tools import BaseTool, Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ---------- SECTION 2: MODEL (Groq) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------- SECTION 3: TOOL CREATION - SUBCLASSING BaseTool ----------
# Most control, most code: every LangChain tool (Tool, StructuredTool) is
# built on BaseTool underneath - subclassing it directly is the "escape hatch"
# for behavior the decorator/StructuredTool shortcuts can't express.
class WordCountInput(BaseModel):
    text: str = Field(description="Text to count words in")


class WordCountTool(BaseTool):
    name: str = "word_count"
    description: str = "Count the number of words in a piece of text."
    args_schema: Type[BaseModel] = WordCountInput

    def _run(self, text: str) -> int:
        return len(text.split())


word_count_tool = WordCountTool()


# ---------- SECTION 4: TOOL CREATION - LEGACY Tool CLASS ----------
# Predates StructuredTool; wraps a function that takes one plain string
# input. Kept for backward compatibility with older codebases.
def shout(text: str) -> str:
    return text.upper() + "!"


shout_tool = Tool(
    name="shout",
    func=shout,
    description="Convert text to uppercase and add an exclamation mark.",
)


# ---------- SECTION 5: DIRECT TOOL INVOCATION (no model, no agent) ----------
# Useful for testing a tool in isolation before wiring it up to an LLM.
print("=== Direct invocation ===")
print(word_count_tool.invoke({"text": "the quick brown fox jumps"}))
print(shout_tool.invoke("hello there"))


# ---------- SECTION 6: TOOL SCHEMA INSPECTION ----------
print("\n=== Schemas ===")
for t in (word_count_tool, shout_tool):
    print(f"- {t.name}: {t.description} | args={t.args}")


# ---------- SECTION 7: LCEL - CHAINING WITH THE PIPE OPERATOR ----------
# prompt | llm | output_parser: each piece is a Runnable, and | feeds the
# output of one directly into the next - no manual glue code in between.
prompt = ChatPromptTemplate.from_template("Summarize this in one sentence: {text}")
chain = prompt | llm | StrOutputParser()

print("\n=== LCEL chain ===")
result = chain.invoke(
    {
        "text": "LangChain lets you connect LLMs to tools, memory, and "
        "external data sources to build agents."
    }
)
print(result)
