# ---------- SECTION 1: IMPORTS ----------
import asyncio
import os
import sys
from pathlib import Path

import mcp.types as types
from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

GROQ_MODEL = "qwen/qwen3.8-27b"
SERVER_SCRIPT = Path(__file__).parent / "10_sampling_server_llm_in_the_loop.py"
groq = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


# ---------- SECTION 2: THE SAMPLING HANDLER ----------
# This is what makes sampling work: when the server's summarize_note tool
# calls ctx.session.create_message(), that request lands HERE, on the
# client. The client - not the server - owns the model and the API key.
async def handle_sampling(
    context: RequestContext[ClientSession, None], params: types.CreateMessageRequestParams
) -> types.CreateMessageResult:
    messages = [{"role": m.role, "content": m.content.text} for m in params.messages]
    if params.systemPrompt:
        messages.insert(0, {"role": "system", "content": params.systemPrompt})

    response = await groq.chat.completions.create(
        model=GROQ_MODEL, messages=messages, max_tokens=params.maxTokens,
    )
    text = response.choices[0].message.content

    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(type="text", text=text),
        model=GROQ_MODEL,
        stopReason="endTurn",
    )


# ---------- SECTION 3: CONNECT WITH THE SAMPLING CALLBACK REGISTERED ----------
async def main():
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=handle_sampling) as session:
            await session.initialize()

            note = (
                "Met with the team about the MCP migration. We agreed to move the notes "
                "tool to Streamable HTTP by Friday, and Priya will write the client-side "
                "sampling handler so the server never needs its own Groq key."
            )
            result = await session.call_tool("summarize_note", {"note_text": note})
            print("Tool asked the client to summarize via sampling.")
            print("Summary:", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
