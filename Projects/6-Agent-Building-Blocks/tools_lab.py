from typing import Type

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, StructuredTool, Tool, tool


# ---------- SECTION 1: @tool WITH TYPE HINTS ----------
@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together and return the sum."""
    return a + b


# ---------- SECTION 2: @tool WITH AN EXPLICIT args_schema ----------
class TemperatureInput(BaseModel):
    celsius: float = Field(description="Temperature in degrees Celsius")


@tool("celsius_to_fahrenheit", args_schema=TemperatureInput)
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32


# ---------- SECTION 3: StructuredTool.from_function ----------
def reverse_text(text: str) -> str:
    return text[::-1]


reverse_text_tool = StructuredTool.from_function(
    func=reverse_text,
    name="reverse_text",
    description="Reverse the characters in a string.",
)


# ---------- SECTION 4: SUBCLASSING BaseTool (most control, most code) ----------
class WordCountInput(BaseModel):
    text: str = Field(description="Text to count words in")


class WordCountTool(BaseTool):
    name: str = "word_count"
    description: str = "Count the number of words in a piece of text."
    args_schema: Type[BaseModel] = WordCountInput

    def _run(self, text: str) -> int:
        return len(text.split())


word_count_tool = WordCountTool()


# ---------- SECTION 5: LEGACY Tool CLASS (single string input) ----------
def shout(text: str) -> str:
    return text.upper() + "!"


shout_tool = Tool(
    name="shout",
    func=shout,
    description="Convert text to uppercase and add an exclamation mark.",
)


TOOLS_BY_NAME = {
    t.name: t
    for t in (add_numbers, celsius_to_fahrenheit, reverse_text_tool, word_count_tool, shout_tool)
}

CREATION_METHOD = {
    "add_numbers": "@tool (type hints only)",
    "celsius_to_fahrenheit": "@tool (explicit args_schema)",
    "reverse_text": "StructuredTool.from_function",
    "word_count": "Subclassing BaseTool",
    "shout": "Legacy Tool class",
}


# ---------- SECTION 6: SCHEMA INSPECTION + DIRECT INVOCATION ----------
def list_tool_schemas() -> list[dict]:
    return [
        {
            "name": t.name,
            "description": t.description,
            "args": t.args,
            "creation_method": CREATION_METHOD[t.name],
        }
        for t in TOOLS_BY_NAME.values()
    ]


def invoke_tool(name: str, tool_input: dict) -> dict:
    tool_obj = TOOLS_BY_NAME[name]
    # Tool (legacy) takes a single string, under whatever key its one arg has
    # (its schema names it "tool_input", not the wrapped function's own
    # parameter name); every other tool here takes the dict as-is.
    payload = next(iter(tool_input.values()), "") if isinstance(tool_obj, Tool) else tool_input
    result = tool_obj.invoke(payload)
    return {"name": name, "input": tool_input, "output": result}
