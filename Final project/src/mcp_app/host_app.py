import json
import sys
from pathlib import Path

import gradio as gr
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import config

SERVER_SCRIPT = Path(__file__).parent / "server.py"
MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = (
    "You are a helpful assistant for California restaurants. Use the available tools "
    "to look up restaurant details, get vibe-based recommendations, and read reviews. "
    "Always ground your answers in tool results rather than guessing."
)

QUICK_START_PROMPTS = [
    "Tell me about Green Papaya",
    "Recommend a romantic restaurant",
    "What do reviewers say about Kimchi Garden?",
]


def _server_params() -> StdioServerParameters:
    return StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])


def mcp_tools_to_groq_format(mcp_tools) -> list[dict]:
    """An MCP Tool already carries an OpenAI-style JSON schema in .inputSchema, so
    wiring it into Groq's function-calling API is a direct pass-through."""
    return [
        {
            "type": "function",
            "function": {"name": t.name, "description": t.description or "", "parameters": t.inputSchema},
        }
        for t in mcp_tools
    ]


async def run_react_loop_with_session(session: ClientSession, groq: AsyncGroq, user_message: str) -> str:
    """The ReAct loop: discover tools -> ask the LLM -> execute any requested tool
    calls against the MCP server -> feed results back -> repeat until a plain-text
    answer comes back with no further tool calls."""
    mcp_tools = (await session.list_tools()).tools
    groq_tools = mcp_tools_to_groq_format(mcp_tools)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(MAX_TOOL_ITERATIONS):
        response = await groq.chat.completions.create(
            model=config.GROQ_TEXT_MODEL,
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
            temperature=0,
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = await session.call_tool(call.function.name, args)
            text = "".join(block.text for block in result.content if block.type == "text")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": text})

    return "I wasn't able to finish that in a reasonable number of steps - try rephrasing your question."


async def run_react_loop(user_message: str) -> str:
    groq = AsyncGroq(api_key=config.require_groq_key())
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await run_react_loop_with_session(session, groq, user_message)


async def respond(message: str, history: list[dict]):
    """Async generator: yields a 'Thinking...' placeholder immediately for instant
    visual feedback, then replaces it with the real answer once the ReAct loop
    finishes."""
    history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": "Thinking..."}]
    yield "", history

    try:
        reply = await run_react_loop(message)
    except Exception as e:
        reply = f"Sorry, something went wrong: {e}"

    history[-1] = {"role": "assistant", "content": reply}
    yield "", history


def build_app() -> gr.Blocks:
    with gr.Blocks(title="California Restaurant MCP Assistant") as demo:
        gr.Markdown("# California Restaurant MCP Assistant")
        gr.Markdown(
            "Ask about restaurants, get vibe-based recommendations, or read reviews - "
            "the agent discovers its tools from an MCP server at runtime."
        )

        chatbot = gr.Chatbot(label="Assistant", latex_delimiters=[])
        msg = gr.Textbox(placeholder="Ask about a restaurant, a vibe, or a review...", label="Your message")

        with gr.Row():
            for prompt in QUICK_START_PROMPTS:
                gr.Button(prompt, size="sm").click(lambda p=prompt: p, outputs=msg)

        with gr.Row():
            submit_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear")

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
        clear_btn.click(lambda: [], None, chatbot)

    return demo


if __name__ == "__main__":
    build_app().launch(server_port=7861)
