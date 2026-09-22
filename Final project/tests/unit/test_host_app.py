import pytest

from mcp_app import host_app

pytestmark = pytest.mark.anyio


class FakeTool:
    def __init__(self, name, description, input_schema):
        self.name = name
        self.description = description
        self.inputSchema = input_schema


class FakeToolsResult:
    def __init__(self, tools):
        self.tools = tools


class FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class FakeCallToolResult:
    def __init__(self, text):
        self.content = [FakeBlock(text)]


class FakeSession:
    def __init__(self, tools, call_tool_response="{}"):
        self._tools = tools
        self._call_tool_response = call_tool_response
        self.calls = []

    async def list_tools(self):
        return FakeToolsResult(self._tools)

    async def call_tool(self, name, args):
        self.calls.append((name, args))
        return FakeCallToolResult(self._call_tool_response)


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none=True):
        d = {"role": "assistant", "content": self.content, "tool_calls": self.tool_calls or None}
        return {k: v for k, v in d.items() if not (exclude_none and v is None)}


class FakeCompletions:
    def __init__(self, responses):
        self._responses = iter(responses)

    async def create(self, **kwargs):
        return type("R", (), {"choices": [type("C", (), {"message": next(self._responses)})()]})()


class FakeGroq:
    def __init__(self, responses):
        self.chat = type("Chat", (), {"completions": FakeCompletions(responses)})()


SAMPLE_TOOLS = [FakeTool("get_restaurant_info", "Look up a restaurant", {"type": "object", "properties": {}})]


def test_mcp_tools_to_groq_format_converts_schema():
    result = host_app.mcp_tools_to_groq_format(SAMPLE_TOOLS)
    assert result == [
        {
            "type": "function",
            "function": {
                "name": "get_restaurant_info",
                "description": "Look up a restaurant",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]


async def test_react_loop_returns_immediately_when_no_tool_call_needed():
    session = FakeSession(SAMPLE_TOOLS)
    groq = FakeGroq([FakeMessage(content="Here's a direct answer.")])

    result = await host_app.run_react_loop_with_session(session, groq, "hi")

    assert result == "Here's a direct answer."
    assert session.calls == []


async def test_react_loop_executes_tool_call_then_returns_final_answer():
    session = FakeSession(SAMPLE_TOOLS, call_tool_response='[{"name": "Green Papaya"}]')
    groq = FakeGroq(
        [
            FakeMessage(tool_calls=[FakeToolCall("call_1", "get_restaurant_info", '{"name": "Green Papaya"}')]),
            FakeMessage(content="Green Papaya is a great Vietnamese spot."),
        ]
    )

    result = await host_app.run_react_loop_with_session(session, groq, "tell me about Green Papaya")

    assert result == "Green Papaya is a great Vietnamese spot."
    assert session.calls == [("get_restaurant_info", {"name": "Green Papaya"})]


async def test_react_loop_gives_up_after_max_iterations():
    session = FakeSession(SAMPLE_TOOLS, call_tool_response="{}")
    always_tool_call = FakeMessage(tool_calls=[FakeToolCall("call_x", "get_restaurant_info", "{}")])
    groq = FakeGroq([always_tool_call] * (host_app.MAX_TOOL_ITERATIONS + 1))

    result = await host_app.run_react_loop_with_session(session, groq, "loop forever")

    assert "wasn't able to finish" in result
    assert len(session.calls) == host_app.MAX_TOOL_ITERATIONS
