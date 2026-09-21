# ---------- SECTION 1: IMPORTS ----------
import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

GROQ_MODEL = "qwen/qwen3.8-27b"
SERVERS_DIR = Path(__file__).parent / "servers"


# ---------- SECTION 2: CONNECT TO EVERY SERVER, PREFIX TOOL NAMES ----------
# A real agent often needs more than one MCP server at once (notes here,
# calculator/weather there, maybe a filesystem or web-search server too).
# Tool names must stay unique across all of them, so each is namespaced as
# "<server>__<tool>" and mapped back to the (session, real name) that owns it.
class MultiServerToolbox:
    def __init__(self):
        self._stack = AsyncExitStack()
        self.route: dict[str, tuple[ClientSession, str]] = {}
        self.groq_tools: list[dict] = []

    async def connect(self, server_name: str, script_path: Path):
        params = StdioServerParameters(command=sys.executable, args=[str(script_path)])
        read, write = await self._stack.enter_async_context(stdio_client(params))
        session = await self._stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        for tool in (await session.list_tools()).tools:
            qualified_name = f"{server_name}__{tool.name}"
            self.route[qualified_name] = (session, tool.name)
            self.groq_tools.append({
                "type": "function",
                "function": {
                    "name": qualified_name,
                    "description": f"[{server_name}] {tool.description or ''}",
                    "parameters": tool.inputSchema,
                },
            })

    async def call(self, qualified_name: str, arguments: dict) -> str:
        session, real_name = self.route[qualified_name]
        result = await session.call_tool(real_name, arguments)
        return "".join(block.text for block in result.content if block.type == "text")

    async def close(self):
        await self._stack.aclose()


# ---------- SECTION 3: SAME AGENT LOOP AS BEFORE, NOW SERVER-AGNOSTIC ----------
async def run_agent(toolbox: MultiServerToolbox, groq: AsyncGroq, user_message: str) -> str:
    messages = [
        {"role": "system", "content": "You can manage notes and also do arithmetic or check the weather."},
        {"role": "user", "content": user_message},
    ]

    for _ in range(5):
        response = await groq.chat.completions.create(
            model=GROQ_MODEL, messages=messages, tools=toolbox.groq_tools, tool_choice="auto", temperature=0,
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"  -> {call.function.name}({args})")
            result_text = await toolbox.call(call.function.name, args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result_text})

    return "Didn't finish in a reasonable number of steps."


# ---------- SECTION 4: WIRE TWO SERVERS INTO ONE AGENT ----------
async def main():
    toolbox = MultiServerToolbox()
    await toolbox.connect("notes", SERVERS_DIR / "notes_server.py")
    await toolbox.connect("utils", SERVERS_DIR / "calculator_and_weather_server.py")
    print("Tools from all connected servers:", [t["function"]["name"] for t in toolbox.groq_tools])

    groq = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    for request in [
        "What's 23 * 17, and also save that number in a note titled 'math answer'?",
        "What's the weather in Bangalore?",
    ]:
        print(f"\nUser: {request}")
        print("Agent:", await run_agent(toolbox, groq, request))

    await toolbox.close()


if __name__ == "__main__":
    asyncio.run(main())
