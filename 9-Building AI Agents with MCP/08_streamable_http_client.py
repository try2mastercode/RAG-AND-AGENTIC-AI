# ---------- SECTION 1: IMPORTS ----------
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


# ---------- SECTION 2: CONNECT OVER HTTP INSTEAD OF SPAWNING A SUBPROCESS ----------
# No StdioServerParameters here - the server is already running on its own
# (start 07_streamable_http_server.py first, in another terminal). The client
# just points at its URL, like calling any other web API.
SERVER_URL = "http://127.0.0.1:8765/mcp"


async def main():
    async with streamablehttp_client(SERVER_URL) as (read, write, _get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            result = await session.call_tool("word_count", {"text": "the model context protocol"})
            print("word_count ->", result.content[0].text)

            result = await session.call_tool("reverse_text", {"text": "mcp"})
            print("reverse_text ->", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
