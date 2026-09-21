# ---------- SECTION 1: IMPORTS ----------
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ---------- SECTION 2: HOW TO REACH THE SERVER ----------
# stdio transport = the client launches the server as a subprocess and talks
# to it over that process's stdin/stdout. This is the same pattern Claude
# Desktop and most local MCP setups use.
SERVER_SCRIPT = Path(__file__).parent / "01_first_mcp_server.py"
server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])


# ---------- SECTION 3: CONNECT, INITIALIZE, CALL TOOLS ----------
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools the server exposes:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            add_result = await session.call_tool("add", {"a": 4, "b": 5})
            print("\nadd(4, 5) ->", add_result.content[0].text)

            greet_result = await session.call_tool("greet", {"name": "Tharun"})
            print("greet('Tharun') ->", greet_result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
