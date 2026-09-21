# ---------- SECTION 1: IMPORTS ----------
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

# allam-2-7b (the .env default) has no tool-calling support on Groq.
GROQ_MODEL = "qwen/qwen3.8-27b"
SERVER_SCRIPT = Path(__file__).parent / "servers" / "notes_server.py"


# ---------- SECTION 2: MCP TOOL SCHEMA -> GROQ FUNCTION SCHEMA ----------
# An MCP Tool already carries an OpenAI-style JSON schema in .inputSchema, so
# wiring it into Groq's function-calling API is a direct pass-through - no
# framework needed to bridge the two.
def mcp_tools_to_groq_format(mcp_tools) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema,
            },
        }
        for t in mcp_tools
    ]


# ---------- SECTION 3: THE MANUAL TOOL-CALLING LOOP ----------
async def run_agent(session: ClientSession, groq: AsyncGroq, groq_tools: list[dict], user_message: str):
    messages = [
        {"role": "system", "content": "You help manage the user's notes using the tools provided."},
        {"role": "user", "content": user_message},
    ]

    for _ in range(5):  # hard cap so a confused model can't loop forever
        response = await groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
            temperature=0,
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content

        # Every tool call the model asks for is forwarded to the MCP server as
        # a real call_tool request - this is the point where the protocol,
        # not a local Python function, actually does the work.
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"  -> MCP call_tool({call.function.name}, {args})")
            result = await session.call_tool(call.function.name, args)
            text = "".join(block.text for block in result.content if block.type == "text")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": text})

    return "Didn't finish in a reasonable number of steps."


# ---------- SECTION 4: WIRE IT TOGETHER ----------
async def main():
    groq = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            groq_tools = mcp_tools_to_groq_format(mcp_tools)

            for request in [
                "Add a note titled 'MCP' with content 'Model Context Protocol connects agents to tools'.",
                "Add a note titled 'Groq' with content 'Fast LLM inference'.",
                "List all my notes.",
            ]:
                print(f"\nUser: {request}")
                reply = await run_agent(session, groq, groq_tools, request)
                print(f"Agent: {reply}")


if __name__ == "__main__":
    asyncio.run(main())
