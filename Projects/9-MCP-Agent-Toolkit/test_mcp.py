"""End-to-end test of the real MCP server (spawned as a subprocess) plus the
Groq-schema bridging in MCPSession — no GROQ_API_KEY or network needed."""
import asyncio
import os
import tempfile

import pytest

from agent import MCPSession

_TEST_DB = os.path.join(tempfile.gettempdir(), "mcp_agent_toolkit_test.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["MCP_DB_PATH"] = _TEST_DB


@pytest.mark.asyncio
async def test_server_roundtrip():
    session = await MCPSession().start()
    try:
        # discovery: the three MCP primitives are all present
        names = {t.name for t in session.mcp_tools}
        assert {"add_task", "list_tasks", "complete_task", "add_note", "calculate"} <= names
        assert {str(r.uri) for r in session.resources} == {"notes://all", "tasks://all"}
        assert {p.name for p in session.prompts} == {"daily_planner"}

        # tool schemas passed straight through as Groq function-calling defs
        add_task_tool = next(t for t in session.groq_tools if t["function"]["name"] == "add_task")
        assert "title" in add_task_tool["function"]["parameters"]["properties"]

        # a real call_tool round trip over stdio
        created = await session.call_tool("add_task", {"title": "write MCP demo", "priority": "high"})
        assert created["title"] == "write MCP demo"
        task_id = created["id"]

        tasks = await session.call_tool("list_tasks", {})
        assert any(t["id"] == task_id for t in tasks)

        completed = await session.call_tool("complete_task", {"task_id": task_id})
        assert completed["done"] == 1

        # resources are read-only, addressed by URI, and reflect the same store
        all_tasks = await session.read_resource("tasks://all")
        assert any(t["id"] == task_id for t in all_tasks)

        # the calculate tool exercises the safe-eval path
        result = await session.call_tool("calculate", {"expression": "12 * (3 + 4)"})
        assert result == 84

        # the prompt template is built server-side from the current open tasks
        prompt_text = await session.get_prompt("daily_planner")
        assert "write MCP demo" not in prompt_text  # it was just completed, so it's no longer "open"

        await session.call_tool("add_task", {"title": "still pending"})
        prompt_text = await session.get_prompt("daily_planner")
        assert "still pending" in prompt_text
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(test_server_roundtrip())
