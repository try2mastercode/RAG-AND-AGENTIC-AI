"""The MCP client + Groq tool-calling agent loop.

Talking to the MCP server is a real protocol round trip, not a local function call:
MCPSession spawns mcp_server.py as a subprocess and speaks MCP over its stdin/stdout
(JSON-RPC messages). The agent loop below asks Groq for a reply, and whenever Groq
asks for a tool, that call is forwarded to the server over that same MCP session.
"""
import json
import os
from contextlib import AsyncExitStack
from datetime import date
from pathlib import Path

from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

GROQ_MODEL = os.getenv("GROQ_MODEL_AGENT", "qwen/qwen3.8-27b")

SYSTEM_PROMPT = """You are a helpful assistant with access to the user's notes and tasks \
through MCP tools. Today is {today}.

Rules:
- Convert relative dates ("tomorrow", "next Friday") to YYYY-MM-DD.
- If the user refers to a task by name, call list_tasks first to find its id.
- Never invent ids, notes or tasks that no tool returned.
- After a tool call, summarize what changed in one or two short sentences.
"""


class MCPSession:
    """Owns the MCP server subprocess + ClientSession, and the Groq-shaped tool list."""

    def __init__(self):
        self._stack = AsyncExitStack()
        self.session: ClientSession | None = None
        self.groq_tools: list[dict] = []
        self.mcp_tools: list = []
        self.resources: list = []
        self.prompts: list = []

    async def start(self):
        # env=None would only inherit a safe allowlist (not MCP_DB_PATH, etc.) - this
        # server is our own trusted code, so give it the full parent environment.
        # Absolute path + explicit cwd: the subprocess inherits the launcher's cwd, which
        # isn't necessarily this file's directory (e.g. uvicorn's --app-dir doesn't chdir).
        server_script = str(Path(__file__).parent / "mcp_server.py")
        server_params = StdioServerParameters(
            command="python", args=[server_script], env=dict(os.environ), cwd=str(Path(__file__).parent)
        )
        read, write = await self._stack.enter_async_context(stdio_client(server_params))
        self.session = await self._stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

        tools = await self.session.list_tools()
        self.mcp_tools = tools.tools
        # MCP tool schemas are already OpenAI-style JSON schema, so wrapping them for
        # Groq's function-calling API is a direct pass-through, not a translation.
        self.groq_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema,
                },
            }
            for t in self.mcp_tools
        ]

        self.resources = (await self.session.list_resources()).resources
        self.prompts = (await self.session.list_prompts()).prompts
        return self

    async def call_tool(self, name: str, arguments: dict) -> dict:
        result = await self.session.call_tool(name, arguments)
        if result.structuredContent is not None:
            content = result.structuredContent
            # FastMCP wraps non-object returns (list, number, ...) as {"result": <value>}
            # since a JSON Schema's top level must be an object - unwrap it back.
            if list(content.keys()) == ["result"]:
                return content["result"]
            return content
        text = "".join(block.text for block in result.content if block.type == "text")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"result": text}

    async def read_resource(self, uri: str):
        result = await self.session.read_resource(uri)
        text = result.contents[0].text
        return json.loads(text)

    async def get_prompt(self, name: str) -> str:
        result = await self.session.get_prompt(name)
        return result.messages[0].content.text

    async def close(self):
        await self._stack.aclose()


async def run_turn(mcp_session: MCPSession, groq: AsyncGroq, history: list[dict]) -> dict:
    """Run one user turn to completion (looping through however many tool calls Groq asks for).

    Returns {"reply": str, "trace": [{"tool", "arguments", "result"}, ...]}.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(today=date.today().isoformat())}, *history]
    trace = []

    for _ in range(8):  # hard cap so a confused model can't loop forever
        response = await groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=mcp_session.groq_tools,
            tool_choice="auto",
            temperature=0,
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return {"reply": msg.content, "trace": trace}

        for call in msg.tool_calls:
            arguments = json.loads(call.function.arguments or "{}")
            result = await mcp_session.call_tool(call.function.name, arguments)
            trace.append({"tool": call.function.name, "arguments": arguments, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })

    return {"reply": "I couldn't finish that in a reasonable number of steps.", "trace": trace}
