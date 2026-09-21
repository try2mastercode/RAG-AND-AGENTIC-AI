# ---------- SECTION 1: IMPORTS ----------
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

SERVERS_DIR = Path(__file__).parent / "servers"


# ---------- SECTION 2: EVERYTHING FROM 06, IN THREE LINES ----------
# 06_multi_server_client_aggregation.py hand-rolled: connecting to each
# server, converting MCP tool schemas, namespacing names, and looping on
# tool_calls. langchain-mcp-adapters + langchain's create_agent do all of
# that for you - this is the framework-integrated version of the same idea.
async def main():
    client = MultiServerMCPClient({
        "notes": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(SERVERS_DIR / "notes_server.py")],
        },
        "utils": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(SERVERS_DIR / "calculator_and_weather_server.py")],
        },
    })
    tools = await client.get_tools()
    print("Tools loaded from both MCP servers:", [t.name for t in tools])

    agent = create_agent(ChatGroq(model="qwen/qwen3.8-27b", temperature=0), tools)

    # ---------- SECTION 3: RUN IT ----------
    result = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "What's the weather in Delhi, and what's 15% of 240?",
        }]
    })
    print("\nFinal answer:", result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
