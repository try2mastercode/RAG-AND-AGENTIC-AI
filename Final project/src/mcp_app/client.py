import asyncio
import sys
from pathlib import Path

import mcp.types as types
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext

import config

SERVER_SCRIPT = Path(__file__).parent / "server.py"


def _project_root_uri() -> str:
    return config.PROJECT_ROOT.as_uri()


async def list_roots_callback(context: RequestContext) -> types.ListRootsResult:
    """Declares the filesystem directory this client is willing to share with the
    server, scoped to the project root (not the whole filesystem)."""
    return types.ListRootsResult(roots=[types.Root(uri=_project_root_uri(), name="capstone-project-root")])


async def handle_sampling(
    context: RequestContext[ClientSession, None], params: types.CreateMessageRequestParams
) -> types.CreateMessageResult:
    """Receives prompts delegated by the server (via ctx.session.create_message()) and
    forwards them to Groq - the client owns the model/API key, never the server."""
    groq = AsyncGroq(api_key=config.require_groq_key())
    messages = [{"role": m.role, "content": m.content.text} for m in params.messages]
    if params.systemPrompt:
        messages.insert(0, {"role": "system", "content": params.systemPrompt})

    response = await groq.chat.completions.create(
        model=config.GROQ_TEXT_MODEL, messages=messages, max_tokens=params.maxTokens or 700
    )
    text = response.choices[0].message.content

    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(type="text", text=text),
        model=config.GROQ_TEXT_MODEL,
        stopReason="endTurn",
    )


def _server_params() -> StdioServerParameters:
    return StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])


async def call_tool(session: ClientSession, name: str, arguments: dict) -> str:
    """Shared helper: tool invocation + JSON-text extraction."""
    result = await session.call_tool(name, arguments)
    return "".join(block.text for block in result.content if block.type == "text")


async def verify_server_capabilities(session: ClientSession) -> tuple[list[str], list[str]]:
    tools = await session.list_tools()
    tool_names = [t.name for t in tools.tools]
    print("Discovered tools:")
    for tool in tools.tools:
        print(f"  - {tool.name}: {tool.description}")

    resources = await session.list_resources()
    resource_uris = [str(r.uri) for r in resources.resources]
    print("\nDiscovered resources:")
    for r in resources.resources:
        print(f"  - {r.uri}")

    return tool_names, resource_uris


async def main():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(
            read, write, list_roots_callback=list_roots_callback, sampling_callback=handle_sampling
        ) as session:
            await session.initialize()

            await verify_server_capabilities(session)
            print(f"\nConfigured roots: [{_project_root_uri()}]")

            print("\nget_restaurant_info('Green Papaya') ->")
            print(await call_tool(session, "get_restaurant_info", {"name": "Green Papaya"}))

            print("\nrecommend_by_vibe('romantic') ->")
            print(await call_tool(session, "recommend_by_vibe", {"vibe": "romantic", "limit": 3}))

            print("\nget_review('Green Papaya') ->")
            print(await call_tool(session, "get_review", {"restaurant_name": "Green Papaya"}))


if __name__ == "__main__":
    asyncio.run(main())
