import json

import pytest

from mcp_app.client import call_tool, verify_server_capabilities, _server_params
from mcp import ClientSession
from mcp.client.stdio import stdio_client


@pytest.mark.anyio
async def test_real_server_exposes_expected_tools_and_resource():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tool_names, resource_uris = await verify_server_capabilities(session)

    assert set(tool_names) == {"get_restaurant_info", "recommend_by_vibe", "get_review"}
    assert "resource://california-culinary-map" in resource_uris


@pytest.mark.anyio
async def test_real_server_get_restaurant_info_returns_json():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await call_tool(session, "get_restaurant_info", {"name": "Green Papaya"})

    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["name"] == "Green Papaya"


@pytest.mark.anyio
async def test_real_server_get_review_returns_json():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await call_tool(session, "get_review", {"restaurant_name": "Green Papaya"})

    data = json.loads(result)
    assert isinstance(data, list)
